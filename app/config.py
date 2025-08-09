import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Dev email mode prints emails to console
    DEV_EMAIL_MODE = True
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "cvlift@gmail.com")
    # Stripe
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
