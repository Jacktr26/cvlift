# app/auth.py
from flask import Blueprint, request, render_template, redirect, url_for, session, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .models import User, db
import os
import sendgrid
from sendgrid.helpers.mail import Mail

bp = Blueprint("auth", __name__)

# --- Helpers ---
def _serializer():
    secret = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret, salt="login")

def _send_login_email(email, token):
    """Send the magic link via SendGrid."""
    base_url = current_app.config.get("BASE_URL", "http://localhost:5000")
    link = url_for("auth.magic", token=token, _external=True, _scheme="https")

    message = Mail(
        from_email=current_app.config["MAIL_FROM"],
        to_emails=email,
        subject="Your CVLift login link",
        html_content=f"Click to sign in: <a href='{link}'>{link}</a>"
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=current_app.config["SENDGRID_API_KEY"])
        sg.send(message)
        current_app.logger.info("Sent login email to %s", email)
    except Exception as e:
        current_app.logger.error("SendGrid error: %s", e)

# --- Routes ---
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            return render_template("login.html", error="Email required")

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()

        token = _serializer().dumps({"uid": user.id})
        _send_login_email(email, token)

        return render_template("login.html", message="Check your email for a login link.")

    return render_template("login.html")


@bp.get("/magic/<token>")
def magic(token):
    try:
        data = _serializer().loads(token, max_age=900)  # 15 min expiry
        uid = int(data["uid"])
    except SignatureExpired:
        current_app.logger.warning("Magic token expired")
        return redirect(url_for("auth.login"))
    except (BadSignature, Exception) as e:
        current_app.logger.warning("Magic token invalid: %s", e)
        return redirect(url_for("auth.login"))

    user = User.query.get(uid)
    if not user:
        current_app.logger.warning("Magic token ok but user id %s not found", uid)
        return redirect(url_for("auth.login"))

    session["uid"] = user.id
    current_app.logger.error("Magic success; set session for uid=%s", user.id)  # temp ERROR for visibility
    return redirect(url_for("routes.dashboard"))


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# --- Debug (remove in prod) ---
@bp.get("/debug/set")
def debug_set():
    session["uid"] = -1
    return "session set"

@bp.get("/debug/whoami")
def debug_whoami():
    return f"uid={session.get('uid')!r}"
