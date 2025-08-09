import stripe
from flask import Blueprint, current_app, request, jsonify, redirect, url_for, session
from .models import db, User, Payment

bp = Blueprint("billing", __name__, url_prefix="/billing")

@bp.before_app_request
def setup_stripe():
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

@bp.route("/checkout")
def checkout():
    user_id = session.get("uid")
    if not user_id: return redirect(url_for("auth.login"))
    price = current_app.config["STRIPE_PRICE_ID"]
    session_obj = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price, "quantity": 1}],
        success_url=f"{current_app.config['BASE_URL']}/billing/success?sid={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{current_app.config['BASE_URL']}/dashboard"
    )
    return redirect(session_obj.url, code=303)

@bp.route("/success")
def success():
    sid = request.args.get("sid")
    if not sid: return redirect(url_for("routes.dashboard"))
    cs = stripe.checkout.Sessions.retrieve(sid)
    user_id = session.get("uid")
    if user_id:
        user = User.query.get(user_id)
        user.credits += 5
        db.session.add(Payment(user_id=user.id, stripe_session=sid, amount=cs.amount_total or 0, credits_added=5))
        db.session.commit()
    return redirect(url_for("routes.dashboard"))

@bp.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()
    return jsonify({"received": True})
