from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import db, User, Doc
from .generate import generate_docs

bp = Blueprint("routes", __name__)

def current_user():
    uid = session.get("uid")
    return User.query.get(uid) if uid else None

@bp.get("/")
def index():
    return render_template("index.html")

@bp.route("/start", methods=["GET", "POST"])
def start():
    user = current_user()
    if not user:
        return redirect(url_for("auth.login"))

    is_demo = request.args.get("demo") == "1"

    if request.method == "POST":
        # In demo mode, skip credit check
        if not is_demo and user.credits <= 0:
            return redirect(url_for("billing.checkout"))

        cv_text = request.form.get("cv_text", "")
        job_url = request.form.get("job_url", "")

        # Generate docs (in-memory for demo)
        job, resume, cover = generate_docs(user, cv_text, job_url)

        # Only save/charge for real jobs
        if not is_demo:
            user.credits -= 1
            db.session.commit()
            return redirect(url_for("routes.result", job_id=job.id))
        else:
            # For demo, store nothing in DB — pass docs in session or re-generate later
            session["demo_docs"] = [
                {"kind": resume.kind, "created_at": resume.created_at, "pdf_path": resume.pdf_path},
                {"kind": cover.kind, "created_at": cover.created_at, "pdf_path": cover.pdf_path}
            ]
            return redirect(url_for("routes.result_demo"))

    return render_template("start.html")

@bp.get("/result/<int:job_id>")
def result(job_id):
    user = current_user()
    if not user:
        return redirect(url_for("auth.login"))
    docs = Doc.query.filter_by(user_id=user.id, job_id=job_id).all()
    return render_template("result.html", docs=docs)

@bp.get("/result-demo")
def result_demo():
    """Show the demo docs from session without saving them in DB."""
    demo_docs = session.get("demo_docs", [])
    return render_template("result.html", docs=demo_docs, demo=True)

@bp.get("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("auth.login"))
    docs = Doc.query.filter_by(user_id=user.id).order_by(Doc.created_at.desc()).all()
    return render_template("dashboard.html", user=user, docs=docs)

@bp.get("/privacy")
def privacy():
    return render_template("privacy.html")

@bp.get("/terms")
def terms():
    return render_template("terms.html")
