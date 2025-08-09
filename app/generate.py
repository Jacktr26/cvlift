from .jd_scrape import fetch_job_details
from .cv_parse import parse_cv_text
from .prompts import draft_resume, draft_cover
from .pdf import html_to_pdf
from .models import db, Job, Doc

def generate_docs(user, cv_text, job_url):
    title, jd_text = fetch_job_details(job_url)
    cv_clean = parse_cv_text(cv_text)

    job = Job(user_id=user.id, url=job_url, title=title, jd_text=jd_text)
    db.session.add(job); db.session.commit()

    resume_html = draft_resume(cv_clean, jd_text, title)
    cover_html  = draft_cover(cv_clean, jd_text, title)

    resume_path = html_to_pdf(resume_html, f"resume_{job.id}")
    cover_path  = html_to_pdf(cover_html,  f"cover_{job.id}")

    d1 = Doc(user_id=user.id, job_id=job.id, kind="resume", html=resume_html, pdf_path=resume_path)
    d2 = Doc(user_id=user.id, job_id=job.id, kind="cover",  html=cover_html,  pdf_path=cover_path)
    db.session.add_all([d1, d2]); db.session.commit()
    return job, d1, d2
