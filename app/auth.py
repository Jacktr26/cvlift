from flask import Blueprint, request, redirect, url_for, session, render_template, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .models import db, User

bp = Blueprint("auth", __name__)

def signer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="magic-link")

def send_email(to, subject, body):
    if current_app.config.get("DEV_EMAIL_MODE", True):
        print(f"\n--- EMAIL (DEV) ---\nTo: {to}\nSubject: {subject}\n\n{body}\n-------------------\n")
        return
    # TODO: add SMTP later

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        token = signer().dumps(email)
        link = url_for("auth.magic", token=token, _external=True)
        send_email(email, "Your CVLift login link", f"Click to sign in: {link}")
        return render_template("login.html", sent=True, email=email)
    return render_template("login.html")

@bp.route("/magic/<token>")
def magic(token):
    try:
        email = signer().loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return "Invalid or expired link", 400
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user); db.session.commit()
    session["uid"] = user.id
    return redirect(url_for("routes.dashboard"))
