import requests
from bs4 import BeautifulSoup

def fetch_job_details(url: str):
    if not url:
        return "Job", ""
    try:
        html = requests.get(url, timeout=8).text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.text.strip()[:200] if soup.title else "Job"
        ps = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))
        return title, ps[:20000]
    except Exception:
        return "Job", ""
