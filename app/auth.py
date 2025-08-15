# app/auth.py
import os
import itsdangerous
from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app, session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import User
from . import db

bp = Blueprint("auth", __name__)

serializer = itsdangerous.URLSafeTimedSerializer(
    os.getenv("SECRET_KEY", "dev-secret")
)

def _send_login_email(email, token):
    """Send a magic login link via SendGrid, or log an error if misconfigured."""
    login_url = f"{current_app.config['BASE_URL']}/magic/{token}"

    mail_from = current_app.config.get("MAIL_FROM")
    api_key = current_app.config.get("SENDGRID_API_KEY")

    if not mail_from or not api_key:
        current_app.logger.error("Email not sent: MAIL_FROM or SENDGRID_API_KEY missing")
        return False

    message = Mail(
        from_email=mail_from,
        to_emails=email,
        subject="Your CVLift login link",
        html_content=f"<p>Click to sign in: <a href='{login_url}'>{login_url}</a></p>",
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as e:
        current_app.logger.error(f"SendGrid error: {e}")
        return False

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        token = serializer.dumps(email, salt="login")

        if not _send_login_email(email, token):
            flash("Could not send login email. Please try again later.", "error")
        else:
            flash("Check your inbox for a login link!", "success")

    return render_template("login.html")

@bp.route("/magic/<token>")
def magic(token):
    try:
        email = serializer.loads(token, salt="login", max_age=600)
    except itsdangerous.BadSignature:
        flash("Invalid or expired link.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    flash("You’re now signed in!", "success")
    return redirect(url_for("routes.dashboard"))
