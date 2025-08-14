# app/config.py
import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email (SendGrid API)
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")  # SG.xxxxx...
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@cvlift.co.uk")

    # Optional: show/hide dev behavior
    ENV = os.environ.get("FLASK_ENV", os.environ.get("ENV", "production"))
