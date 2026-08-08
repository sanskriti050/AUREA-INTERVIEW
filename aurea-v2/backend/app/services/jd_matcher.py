"""Job Description ↔ Resume matcher using TF-IDF cosine similarity."""
from __future__ import annotations
import re
from collections import Counter
import math


STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","have","has","had","do","does","did",
    "will","would","could","should","may","might","shall","can","need","must",
    "we","our","you","your","they","their","it","its","this","that","these",
    "those","i","my","me","him","her","his","hers","us","them","who","which",
    "what","when","where","how","why","not","no","nor","so","yet","both",
    "either","neither","each","every","all","any","few","more","most","other",
    "such","than","too","very","just","about","above","after","before","between",
}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]*\b", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def _tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = Counter(tokens)
    total = len(tokens) or 1
    return {w: (count / total) * idf.get(w, 1.0) for w, count in tf.items()}


def _cosine(v1: dict, v2: dict) -> float:
    keys = set(v1) & set(v2)
    dot = sum(v1[k] * v2[k] for k in keys)
    mag1 = math.sqrt(sum(x * x for x in v1.values())) or 1
    mag2 = math.sqrt(sum(x * x for x in v2.values())) or 1
    return dot / (mag1 * mag2)


def match_jd(resume_text: str, jd_text: str) -> dict:
    resume_tokens = _tokenize(resume_text)
    jd_tokens = _tokenize(jd_text)

    # Build simple IDF from both documents
    all_docs = [set(resume_tokens), set(jd_tokens)]
    df = Counter(w for doc in all_docs for w in doc)
    n = len(all_docs)
    idf = {w: math.log((n + 1) / (df[w] + 1)) + 1 for w in df}

    rv = _tfidf_vector(resume_tokens, idf)
    jv = _tfidf_vector(jd_tokens, idf)

    similarity = _cosine(rv, jv)
    match_score = min(100, round(similarity * 160))  # scale to 0-100

    resume_words = set(resume_tokens)
    jd_words = set(jd_tokens)

    matched = sorted(resume_words & jd_words, key=lambda w: jv.get(w, 0), reverse=True)[:20]
    missing = sorted(jd_words - resume_words, key=lambda w: jv.get(w, 0), reverse=True)[:15]

    suggestions = []
    if missing:
        suggestions.append(f"Add these keywords from the JD: {', '.join(missing[:8])}.")
    if match_score < 50:
        suggestions.append("Your resume content has low overlap with this JD. Tailor your skills and project descriptions.")
    elif match_score < 70:
        suggestions.append("Good overlap. Strengthen the experience section with role-specific terminology.")
    else:
        suggestions.append("Strong match. Ensure your top bullets mirror the JD's priority skills.")

    return {
        "match_score": match_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
    }
