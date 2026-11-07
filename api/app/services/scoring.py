"""Explainable candidate scoring against a job rubric.

Protected attributes (name, photo, gender, age, religion, caste, nationality)
are never used as inputs to this function.
"""
from __future__ import annotations
from dataclasses import dataclass

PROTECTED_ATTRIBUTES = {"name", "photo", "gender", "age", "religion", "caste", "nationality", "race", "ethnicity"}


@dataclass
class ScoreComponent:
    score: float          # 0-100
    weight: float         # 0-1
    evidence: list[dict]  # [{text, url}]


@dataclass
class CandidateScore:
    total_score: float
    components: dict[str, ScoreComponent]


def _skill_overlap(candidate_skills: list[str], required_skills: list[str]) -> tuple[float, list[str]]:
    if not required_skills:
        return 100.0, []
    cs = {s.lower() for s in candidate_skills}
    rs = {s.lower() for s in required_skills}
    matched = list(cs & rs)
    score = (len(matched) / len(rs)) * 100
    return score, matched


def score_candidate(
    candidate_skills: list[str],
    candidate_title: str | None,
    candidate_location: str | None,
    candidate_employer: str | None,
    candidate_profile_urls: dict,
    candidate_raw_sources: list[dict],
    rubric: dict,
    search_spec: dict,
) -> CandidateScore:
    """
    Compute explainable score. Inputs must NOT include protected attributes.
    rubric: {criteria: [{name, weight, must_have}], ...}
    search_spec: {titles, skills_must, skills_nice, location, exclusions}
    """
    skills_must = search_spec.get("skills_must", [])
    skills_nice = search_spec.get("skills_nice", [])
    target_titles = search_spec.get("titles", [])
    target_location = search_spec.get("location")

    # Primary skill match
    primary_score, primary_matched = _skill_overlap(candidate_skills, skills_must)
    primary_evidence = [{"text": f"Matched skills: {', '.join(primary_matched)}", "url": None}] if primary_matched else []

    # Secondary skill match
    secondary_score, secondary_matched = _skill_overlap(candidate_skills, skills_nice)
    secondary_evidence = [{"text": f"Nice-to-have skills: {', '.join(secondary_matched)}", "url": None}] if secondary_matched else []

    # Title / experience fit
    experience_score = 0.0
    experience_evidence = []
    if candidate_title and target_titles:
        ct = candidate_title.lower()
        for t in target_titles:
            if t.lower() in ct or ct in t.lower():
                experience_score = 80.0
                experience_evidence = [{"text": f"Title '{candidate_title}' matches '{t}'", "url": None}]
                break
        if not experience_score and candidate_title:
            experience_score = 40.0

    # Domain fit — approximate: employer in a known product/tech company
    domain_score = 50.0
    domain_evidence = []
    if candidate_employer:
        product_cos = {"zomato", "swiggy", "razorpay", "phonepe", "cred", "meesho", "ola", "paytm", "freshworks", "fractal"}
        if any(c in candidate_employer.lower() for c in product_cos):
            domain_score = 85.0
            domain_evidence = [{"text": f"Product company: {candidate_employer}", "url": None}]
        else:
            domain_score = 55.0

    # Location fit
    location_score = 50.0
    location_evidence = []
    if target_location and candidate_location:
        if target_location.lower() in candidate_location.lower() or candidate_location.lower() in target_location.lower():
            location_score = 95.0
            location_evidence = [{"text": f"Location match: {candidate_location}", "url": None}]
    elif not target_location:
        location_score = 75.0

    # Recency — has any public source URL
    recency_score = 60.0
    recency_evidence = []
    if candidate_profile_urls:
        recency_score = 80.0
        url = next(iter(candidate_profile_urls.values()), None)
        recency_evidence = [{"text": "Active public profile", "url": url}]

    # Build weighted total (default weights if rubric not provided)
    default_weights = {
        "primary_skill": 0.35,
        "secondary_skill": 0.15,
        "experience": 0.20,
        "domain": 0.10,
        "location": 0.10,
        "recency": 0.10,
    }

    components = {
        "primary_skill": ScoreComponent(primary_score, default_weights["primary_skill"], primary_evidence),
        "secondary_skill": ScoreComponent(secondary_score, default_weights["secondary_skill"], secondary_evidence),
        "experience": ScoreComponent(experience_score, default_weights["experience"], experience_evidence),
        "domain": ScoreComponent(domain_score, default_weights["domain"], domain_evidence),
        "location": ScoreComponent(location_score, default_weights["location"], location_evidence),
        "recency": ScoreComponent(recency_score, default_weights["recency"], recency_evidence),
    }

    total = sum(c.score * c.weight for c in components.values())

    return CandidateScore(total_score=round(total, 2), components=components)


def components_to_dict(score: CandidateScore) -> dict:
    return {
        name: {
            "score": c.score,
            "weight": c.weight,
            "evidence": c.evidence,
        }
        for name, c in score.components.items()
    }
