from app.services.resume_parser import analyze_resume


def test_section_detection_recognizes_common_resume_heading_variants():
    text = """Asha Sharma
Professional Summary
Aspiring software engineer with Python and SQL experience.
Technical Skills: Python, SQL, FastAPI, Git
Work Experience: Developer Intern, 2024 - Present
Selected Projects: Built and deployed a FastAPI service.
Education: B.Tech Computer Science
Certificates: Cloud Fundamentals
"""
    sections = analyze_resume(text)["sections"]
    assert all(sections.values())
