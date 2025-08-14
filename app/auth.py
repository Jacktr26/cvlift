# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import db, User

bp = Blueprint("auth", __name__)

def _serializer():
    # Separate salt so these tokens can't collide with others
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="magic-login")

def _send_magic_email(to_email: str, link: str) -> bool:
    """Send magic link via SendGrid. Returns True on HTTP 2xx."""
    api_key = current_app.config.get("SENDGRID_API_KEY")
    sender  = current_app.config.get("MAIL_DEFAULT_SENDER")

    if not api_key:
        current_app.logger.error("SENDGRID_API_KEY missing from config/env")
        return False
    if not sender:
        current_app.logger.error("MAIL_DEFAULT_SENDER missing from config/env")
        return False

    message = Mail(
        from_email=sender,
        to_emails=to_email,
        subject="Your CVLift sign-in link",
        html_content=(
            f"<p>Click to sign in:</p>"
            f"<p><a href='{link}'>{link}</a></p>"
            f"<p style='color:#666'>This link expires in 15 minutes.</p>"
        ),
    )

    try:
        sg = SendGridAPIClient(api_key)
        resp = sg.send(message)
        current_app.logger.info("SendGrid status: %s", resp.status_code)
        return 200 <= resp.status_code < 300
    except Exception as e:
        current_app.logger.error("SendGrid error: %s", e)
        return False

@bp.route("/login", methods=["GET", "POST"])
def login():
    """Request a magic link. Creates the user on first login."""
    sent = False
    email = None

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if not email:
            return render_template("login.html", sent=False, email=None)

        # find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, credits=0)
            db.session.add(user)
            db.session.commit()

        # mint token & absolute URL
        token = _serializer().dumps({"uid": user.id})
        link = url_for("auth.magic", token=token, _external=True)

        sent = _send_magic_email(email, link)

    return render_template("login.html", sent=sent, email=email)

@bp.get("/magic/<token>")
def magic(token):
    """Consume magic link; log the user in."""
    try:
        data = _serializer().loads(token, max_age=900)  # 15 minutes
        uid = int(data["uid"])
    except (SignatureExpired, BadSignature, KeyError, ValueError):
        current_app.logger.warning("Invalid/expired magic token")
        return redirect(url_for("auth.login"))

    user = User.query.get(uid)
    if not user:
        current_app.logger.warning("Token for missing user id=%s", uid)
        return redirect(url_for("auth.login"))

    session["uid"] = user.id
    return redirect(url_for("routes.dashboard"))

@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.index"))
