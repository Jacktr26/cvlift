# app/config.py
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    MAIL_FROM = os.getenv("MAIL_FROM", "no-reply@cvlift.com")

    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    BASE_URL = os.getenv("BASE_URL", "https://cvlift.onrender.com")
