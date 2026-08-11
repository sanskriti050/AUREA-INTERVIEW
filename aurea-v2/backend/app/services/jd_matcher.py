"""Explainable, skill-first resume ↔ job-description matching.

This deliberately avoids scoring random word overlap. It maps both documents
to a shared technical-skill taxonomy, then reports evidence and genuine gaps.
"""
from __future__ import annotations

import re

from app.services.resume_parser import detect_skills


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "is", "are", "was", "were", "be", "been", "have", "has", "had", "will", "would", "could",
    "should", "may", "might", "can", "must", "we", "our", "you", "your", "they", "their",
    "this", "that", "these", "those", "from", "into", "about", "through", "across", "within",
    "job", "jobs", "role", "roles", "position", "positions", "candidate", "candidates", "company",
    "team", "teams", "work", "working", "opportunity", "responsibilities", "responsibility",
    "requirements", "requirement", "qualified", "qualification", "experience", "years", "year",
    "including", "ability", "skills", "skill", "knowledge", "looking", "seeking", "preferred",
}


def _meaningful_terms(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]*\b", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


def _lexical_evidence(resume_text: str, jd_text: str) -> float:
    """A small secondary signal; never the primary score."""
    resume_terms, jd_terms = set(_meaningful_terms(resume_text)), set(_meaningful_terms(jd_text))
    if not jd_terms:
        return 0.0
    return len(resume_terms & jd_terms) / len(jd_terms)


def _role_hint(jd_text: str) -> str:
    text = jd_text.lower()
    for label, phrases in (
        ("Machine Learning", ("machine learning", "ml engineer", "data scientist")),
        ("Data", ("data analyst", "data engineer", "analytics")),
        ("Backend", ("backend", "back-end", "api developer")),
        ("Frontend", ("frontend", "front-end", "ui developer")),
        ("Software Engineering", ("software engineer", "full stack", "fullstack")),
    ):
        if any(phrase in text for phrase in phrases):
            return label
    return "this role"


def match_jd(resume_text: str, jd_text: str) -> dict:
    """Return a stable ATS-style score with skills the user can act on."""
    resume_skills = set(detect_skills(resume_text))
    required_skills = set(detect_skills(jd_text))
    matched = sorted(resume_skills & required_skills)
    missing = sorted(required_skills - resume_skills)
    coverage = len(matched) / len(required_skills) if required_skills else 0.0
    lexical = _lexical_evidence(resume_text, jd_text)

    if not required_skills:
        return {
            "match_score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "skill_coverage": 0,
            "matched_skill_count": 0,
            "required_skill_count": 0,
            "analysis_summary": "No recognised technical requirements were found. Paste the complete JD, including tools, responsibilities, and qualifications, for a reliable comparison.",
            "suggestions": [
                "Add the complete responsibilities and required-skills sections from the job description.",
                "A job title alone is not enough to generate an ATS-style match score.",
            ],
        }

    # Skill coverage drives 85% of the outcome; wording overlap only checks that
    # the resume includes relevant evidence beyond a list of tools.
    match_score = round(min(100, 12 + coverage * 78 + min(lexical, 0.5) * 20))
    role = _role_hint(jd_text)
    summary = (
        f"Your resume demonstrates {len(matched)} of {len(required_skills)} recognised skills requested for {role}. "
        f"The strongest evidence is {', '.join(matched[:4]) or 'not yet explicit'}."
    )

    suggestions = []
    if missing:
        suggestions.append(f"Only add {', '.join(missing[:5])} if you can support it with real coursework, project, or internship evidence.")
    if coverage < 0.5:
        suggestions.append("Tailor the project bullets near the top of your resume to show the most relevant tools, problem, action, and measurable result.")
    elif coverage < 0.8:
        suggestions.append("Good skill coverage. Strengthen the matched skills with outcomes, scale, and ownership in your experience or projects.")
    else:
        suggestions.append("Strong skill coverage. Mirror the JD's most important terminology in your summary and top project bullets—only where truthful.")

    return {
        "match_score": match_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "skill_coverage": round(coverage * 100),
        "matched_skill_count": len(matched),
        "required_skill_count": len(required_skills),
        "analysis_summary": summary,
        "suggestions": suggestions,
    }
