from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import db, User, Doc
from .generate import generate_docs

bp = Blueprint("routes", __name__)

def current_user():
    uid = session.get("uid")
    return User.query.get(uid) if uid else None

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/start", methods=["GET","POST"])
def start():
    user = current_user()
    if not user:
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        if user.credits <= 0:
            return redirect(url_for("billing.checkout"))
        cv_text = request.form.get("cv_text","")
        job_url = request.form.get("job_url","")
        job, resume, cover = generate_docs(user, cv_text, job_url)
        user.credits -= 1; db.session.commit()
        return redirect(url_for("routes.result", job_id=job.id))
    return render_template("start.html")

@bp.route("/result/<int:job_id>")
def result(job_id):
    user = current_user()
    if not user: return redirect(url_for("auth.login"))
    docs = Doc.query.filter_by(user_id=user.id, job_id=job_id).all()
    return render_template("result.html", docs=docs)

@bp.route("/dashboard")
def dashboard():
    user = current_user()
    if not user: return redirect(url_for("auth.login"))
    docs = Doc.query.filter_by(user_id=user.id).order_by(Doc.created_at.desc()).all()
    return render_template("dashboard.html", user=user, docs=docs)
