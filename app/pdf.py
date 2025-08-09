import os, pdfkit

def html_to_pdf(html: str, basename: str, out_dir: str = "instance"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{basename}.pdf")
    try:
        pdfkit.from_string(html, path)  # needs wkhtmltopdf in prod
        return path
    except Exception:
        # fallback to HTML if pdf isn't available
        hpath = os.path.join(out_dir, f"{basename}.html")
        with open(hpath, "w", encoding="utf-8") as f:
            f.write(html)
        return hpath
