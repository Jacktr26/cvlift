def draft_resume(cv_text, jd_text, title):
    return f"""
<h1>Resume – tailored for {title}</h1>
<h2>Summary</h2>
<p>Motivated candidate aligning experience to the role.</p>
<h2>Key Matches</h2>
<ul>
<li>Skill A → Job requirement A</li>
<li>Skill B → Job requirement B</li>
</ul>
"""

def draft_cover(cv_text, jd_text, title):
    return f"""
<h1>Cover letter – {title}</h1>
<p>Dear Hiring Manager,</p>
<p>I’m excited to apply for {title}. My experience maps strongly to your needs. (dev mode text)</p>
<p>Best,</p>
<p>Cand.</p>
"""
