# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import db, User

bp = Blueprint("auth", __name__)

def _ts():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="magic-login")

def send_magic_email(to_email: str, link: str) -> bool:
    message = Mail(
        from_email=current_app.config["MAIL_DEFAULT_SENDER"],
        to_emails=to_email,
        subject="Your CVLift login link",
        html_content=f"<p>Click to sign in: <a href='{link}'>{link}</a></p><p style='color:#666'>Expires in 15 minutes.</p>",
    )
    try:
        sg = SendGridAPIClient(current_app.config["SENDGRID_API_KEY"])
        resp = sg.send(message)  # 202 is success
        current_app.logger.info("SendGrid status: %s", resp.status_code)
        return 200 <= resp.status_code < 300
    except Exception as e:
        current_app.logger.error("SendGrid error: %s", e)
        return False

@bp.route("/login", methods=["GET", "POST"])
def login():
    sent = False
    email = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        if not email:
            return render_template("login.html", sent=False, email=None)

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, credits=0)
            db.session.add(user)
            db.session.commit()

        token = _ts().dumps({"uid": user.id})
        link = url_for("auth.magic", token=token, _external=True)

        # Always send via SendGrid in prod
        sent = send_magic_email(email, link)

    return render_template("login.html", sent=sent, email=email)

@bp.get("/magic/<token>")
def magic(token):
    try:
        data = _ts().loads(token, max_age=900)
        uid = int(data["uid"])
    except (SignatureExpired, BadSignature, KeyError, ValueError):
        return redirect(url_for("auth.login"))
    session["uid"] = uid
    return redirect(url_for("routes.dashboard"))
