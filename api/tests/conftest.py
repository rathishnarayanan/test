"""Shared fixtures for the test suite."""
import pytest
from app.adapters.base import SearchQuery


@pytest.fixture
def search_spec():
    return {
        "titles": ["Senior Python Engineer", "Backend Engineer"],
        "skills_must": ["python", "fastapi", "postgresql"],
        "skills_nice": ["redis", "celery", "docker"],
        "location": "Bangalore",
        "exclusions": [],
    }


@pytest.fixture
def rubric():
    return {
        "criteria": [
            {"name": "primary_skill", "weight": 0.35, "must_have": True},
            {"name": "secondary_skill", "weight": 0.15, "must_have": False},
            {"name": "experience", "weight": 0.20, "must_have": False},
            {"name": "domain", "weight": 0.10, "must_have": False},
            {"name": "location", "weight": 0.10, "must_have": False},
            {"name": "recency", "weight": 0.10, "must_have": False},
        ]
    }


@pytest.fixture
def sample_query():
    return SearchQuery(
        titles=["Software Engineer"],
        skills_must=["python"],
        skills_nice=["react"],
        location="Bangalore",
        exclusions=[],
        limit=20,
    )
