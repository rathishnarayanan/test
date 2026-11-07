"""Tests for the explainable scoring service."""
import pytest
from app.services.scoring import score_candidate, PROTECTED_ATTRIBUTES, components_to_dict


SAMPLE_RUBRIC = {
    "criteria": [
        {"name": "primary_skill", "weight": 0.35, "must_have": True},
        {"name": "secondary_skill", "weight": 0.15, "must_have": False},
        {"name": "experience", "weight": 0.20, "must_have": False},
        {"name": "domain", "weight": 0.10, "must_have": False},
        {"name": "location", "weight": 0.10, "must_have": False},
        {"name": "recency", "weight": 0.10, "must_have": False},
    ]
}

SAMPLE_SPEC = {
    "titles": ["Senior Python Engineer", "Backend Engineer"],
    "skills_must": ["python", "fastapi", "postgresql"],
    "skills_nice": ["redis", "celery", "docker"],
    "location": "Bangalore",
    "exclusions": [],
}


def test_score_full_match():
    """Perfect candidate gets a high score."""
    result = score_candidate(
        candidate_skills=["python", "fastapi", "postgresql", "redis", "celery"],
        candidate_title="Senior Python Engineer",
        candidate_location="Bangalore, India",
        candidate_employer="Razorpay",
        candidate_profile_urls={"github": "https://github.com/testuser"},
        candidate_raw_sources=[],
        rubric=SAMPLE_RUBRIC,
        search_spec=SAMPLE_SPEC,
    )
    assert result.total_score >= 75
    assert result.components["primary_skill"].score == 100.0
    assert result.components["location"].score == 95.0


def test_score_no_skills():
    """Candidate with zero required skills gets low primary skill score."""
    result = score_candidate(
        candidate_skills=["java", "spring"],
        candidate_title=None,
        candidate_location=None,
        candidate_employer=None,
        candidate_profile_urls={},
        candidate_raw_sources=[],
        rubric=SAMPLE_RUBRIC,
        search_spec=SAMPLE_SPEC,
    )
    assert result.components["primary_skill"].score == 0.0
    assert result.total_score < 40


def test_score_partial_skills():
    """Partial skill match gives proportional score."""
    result = score_candidate(
        candidate_skills=["python"],  # 1 of 3 must-have
        candidate_title=None,
        candidate_location=None,
        candidate_employer=None,
        candidate_profile_urls={},
        candidate_raw_sources=[],
        rubric=SAMPLE_RUBRIC,
        search_spec=SAMPLE_SPEC,
    )
    # 1/3 ≈ 33.33
    assert abs(result.components["primary_skill"].score - 33.33) < 1.0


def test_score_location_no_requirement():
    """When no target location, location score is 75."""
    spec = {**SAMPLE_SPEC, "location": None}
    result = score_candidate(
        candidate_skills=[],
        candidate_title=None,
        candidate_location="Mumbai",
        candidate_employer=None,
        candidate_profile_urls={},
        candidate_raw_sources=[],
        rubric=SAMPLE_RUBRIC,
        search_spec=spec,
    )
    assert result.components["location"].score == 75.0


def test_protected_attributes_not_in_scoring_inputs():
    """Verify protected attribute constant contains the right fields."""
    for attr in ("name", "gender", "age", "religion", "caste", "race", "ethnicity", "nationality"):
        assert attr in PROTECTED_ATTRIBUTES


def test_score_uses_no_protected_attribute():
    """score_candidate signature must not accept protected attributes."""
    import inspect
    sig = inspect.signature(score_candidate)
    params = set(sig.parameters.keys())
    for attr in PROTECTED_ATTRIBUTES:
        assert attr not in params, f"Protected attribute '{attr}' found in score_candidate signature"


def test_components_to_dict_shape():
    result = score_candidate(
        candidate_skills=["python"],
        candidate_title="Engineer",
        candidate_location="Bangalore",
        candidate_employer="Razorpay",
        candidate_profile_urls={"github": "https://github.com/x"},
        candidate_raw_sources=[],
        rubric=SAMPLE_RUBRIC,
        search_spec=SAMPLE_SPEC,
    )
    d = components_to_dict(result)
    for key, val in d.items():
        assert "score" in val
        assert "weight" in val
        assert "evidence" in val
        assert isinstance(val["evidence"], list)


def test_score_total_is_weighted_sum():
    """total_score must equal the sum of score*weight for all components."""
    result = score_candidate(
        candidate_skills=["python", "fastapi"],
        candidate_title="Backend Engineer",
        candidate_location="Bangalore",
        candidate_employer="Freshworks",
        candidate_profile_urls={"github": "https://github.com/x"},
        candidate_raw_sources=[],
        rubric=SAMPLE_RUBRIC,
        search_spec=SAMPLE_SPEC,
    )
    expected = sum(c.score * c.weight for c in result.components.values())
    assert abs(result.total_score - round(expected, 2)) < 0.01
