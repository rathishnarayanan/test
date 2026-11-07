"""Tests for mock adapters — deterministic fixtures, adapter interface compliance."""
import asyncio
import pytest
from app.adapters.base import SearchQuery, Person, OutreachMessage, CallRequest
from app.adapters.sources.mock import MockSourceAdapter
from app.adapters.sources.devto import DevToAdapter
from app.adapters.sources.npm import NpmAdapter
from app.adapters.sources.google_cse import GoogleCSEAdapter
from app.adapters.contact.mock import MockContactAdapter
from app.adapters.llm.mock import MockLLMAdapter
from app.adapters.outreach.mock import MockOutreachAdapter
from app.adapters.telephony.mock import MockTelephonyAdapter
from app.adapters.interview.mock import MockInterviewAdapter
from app.adapters.embedding.mock import MockEmbeddingAdapter


SAMPLE_QUERY = SearchQuery(
    titles=["Software Engineer"],
    skills_must=["python"],
    skills_nice=["react"],
    location="Bangalore",
    exclusions=[],
    limit=10,
)


# ── Source adapter ──────────────────────────────────────────────────────────

def test_mock_source_returns_profiles():
    profiles = asyncio.run(MockSourceAdapter().search(SAMPLE_QUERY))
    assert len(profiles) > 0


def test_mock_source_respects_limit():
    query = SearchQuery(titles=[], skills_must=[], skills_nice=[], location=None, exclusions=[], limit=3)
    profiles = asyncio.run(MockSourceAdapter().search(query))
    assert len(profiles) <= 3


def test_mock_source_profiles_have_required_fields():
    profiles = asyncio.run(MockSourceAdapter().search(SAMPLE_QUERY))
    for p in profiles:
        assert p.full_name
        assert p.adapter_name == "mock"


def test_mock_source_filters_by_skill():
    query_no_match = SearchQuery(
        titles=[], skills_must=["COBOL", "FORTRAN"], skills_nice=[], location=None, exclusions=[], limit=50
    )
    profiles = asyncio.run(MockSourceAdapter().search(query_no_match))
    assert len(profiles) == 0 or all(
        any(s.lower() in ["cobol", "fortran"] for s in p.skills) for p in profiles
    )


# ── LLM adapter ─────────────────────────────────────────────────────────────

def test_mock_llm_jd_parse():
    response = asyncio.run(MockLLMAdapter().complete("jd_parse", {"jd_text": "Looking for a Python engineer"}))
    assert "titles" in response.result
    assert "skills_must" in response.result
    assert response.mock is True


def test_mock_llm_rule_parse():
    response = asyncio.run(MockLLMAdapter().complete("rule_parse", {"natural_language": "must have 5 years experience"}))
    assert "field" in response.result or "operator" in response.result or isinstance(response.result, dict)


def test_mock_llm_unknown_prompt_returns_empty():
    response = asyncio.run(MockLLMAdapter().complete("nonexistent_prompt", {}))
    assert isinstance(response.result, dict)


# ── Outreach adapter ─────────────────────────────────────────────────────────

def test_mock_outreach_send():
    msg = OutreachMessage(
        candidate_id="cand-1",
        role_id="role-1",
        workspace_id="ws-1",
        channel="whatsapp",
        template_name="outreach_whatsapp",
        variables={"name": "Test User"},
    )
    result = asyncio.run(MockOutreachAdapter().send(msg))
    assert result.message_id.startswith("mock_")
    assert result.success is True


# ── Contact adapter ──────────────────────────────────────────────────────────

def test_mock_contact_find():
    person = Person(full_name="Anjali Sharma", current_employer="Razorpay")
    result = asyncio.run(MockContactAdapter().find_contact(person))
    assert result.found is True
    assert len(result.emails) > 0
    email_val = result.emails[0]["value"]
    assert "***" in email_val, "Contact email should be masked"


def test_mock_contact_verify_email():
    result = asyncio.run(MockContactAdapter().verify_email("test@example.com"))
    assert result is True


# ── Telephony adapter ────────────────────────────────────────────────────────

def test_mock_telephony_call():
    req = CallRequest(
        candidate_id="cand-1",
        role_id="role-1",
        workspace_id="ws-1",
        to_number="+919876543210",
        call_type="screening",
        questions=["Tell me about yourself"],
    )
    result = asyncio.run(MockTelephonyAdapter().place_call(req))
    assert result.call_id.startswith("mock_call_")
    assert result.transcript
    assert all(a["score"] >= 0 for a in result.answers)


# ── Interview adapter ────────────────────────────────────────────────────────

def test_mock_interview_call():
    req = CallRequest(
        candidate_id="cand-1",
        role_id="role-1",
        workspace_id="ws-1",
        to_number="+919876543210",
        call_type="interview",
        questions=[{"skill": "python", "question": "Explain decorators"}],
    )
    result = asyncio.run(MockInterviewAdapter().place_call(req))
    assert result.call_id.startswith("mock_interview_")
    assert result.transcript


# ── Embedding adapter ────────────────────────────────────────────────────────

def test_mock_embedding_dimension():
    result = asyncio.run(MockEmbeddingAdapter().embed("Python developer with FastAPI experience"))
    assert len(result.vector) == 768


def test_mock_embedding_deterministic():
    text = "Same text produces same vector"
    r1 = asyncio.run(MockEmbeddingAdapter().embed(text))
    r2 = asyncio.run(MockEmbeddingAdapter().embed(text))
    assert r1.vector == r2.vector


def test_mock_embedding_different_texts():
    r1 = asyncio.run(MockEmbeddingAdapter().embed("Python developer"))
    r2 = asyncio.run(MockEmbeddingAdapter().embed("Java developer"))
    assert r1.vector != r2.vector


def test_mock_embedding_unit_length():
    import math
    result = asyncio.run(MockEmbeddingAdapter().embed("test"))
    magnitude = math.sqrt(sum(v * v for v in result.vector))
    assert abs(magnitude - 1.0) < 0.001


# ── DevTo adapter (interface compliance — no live call in unit tests) ─────────

def test_devto_adapter_is_source_adapter():
    from app.adapters.base import SourceAdapter
    assert issubclass(DevToAdapter, SourceAdapter)


def test_devto_adapter_instantiates():
    adapter = DevToAdapter()
    assert adapter is not None


def test_devto_adapter_empty_query_returns_list():
    query = SearchQuery(titles=[], skills_must=[], skills_nice=[], location=None, exclusions=[], limit=5)
    result = asyncio.run(DevToAdapter().search(query))
    assert isinstance(result, list)


# ── npm adapter (interface compliance) ───────────────────────────────────────

def test_npm_adapter_is_source_adapter():
    from app.adapters.base import SourceAdapter
    assert issubclass(NpmAdapter, SourceAdapter)


def test_npm_adapter_instantiates():
    adapter = NpmAdapter()
    assert adapter is not None


def test_npm_adapter_empty_query_returns_list():
    query = SearchQuery(titles=[], skills_must=[], skills_nice=[], location=None, exclusions=[], limit=5)
    result = asyncio.run(NpmAdapter().search(query))
    assert isinstance(result, list)


# ── Google CSE adapter (no-key graceful no-op) ───────────────────────────────

def test_google_cse_adapter_is_source_adapter():
    from app.adapters.base import SourceAdapter
    assert issubclass(GoogleCSEAdapter, SourceAdapter)


def test_google_cse_no_keys_returns_empty():
    query = SearchQuery(
        titles=["Software Engineer"],
        skills_must=["python"],
        skills_nice=[],
        location="Bangalore",
        exclusions=[],
        limit=10,
    )
    result = asyncio.run(GoogleCSEAdapter().search(query))
    assert result == []
