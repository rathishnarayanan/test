"""Tests for entity resolution — merging duplicate profiles."""
import pytest
from app.adapters.base import RawProfile
from app.services.entity_resolution import resolve_profiles, _name_similarity, _merge_confidence


def _profile(name, employer=None, title=None, location=None, skills=None, github=None, so=None, adapter="mock"):
    urls = {}
    if github:
        urls["github"] = f"https://github.com/{github}"
    if so:
        urls["stackoverflow"] = f"https://stackoverflow.com/users/{so}"
    return RawProfile(
        adapter_name=adapter,
        source_url=None,
        full_name=name,
        current_title=title,
        current_employer=employer,
        location=location,
        skills=skills or [],
        profile_urls=urls,
        raw_data={},
    )


def test_identical_profiles_merged():
    profiles = [
        _profile("Anjali Sharma", employer="Razorpay", github="anjali"),
        _profile("Anjali Sharma", employer="Razorpay", github="anjali"),
    ]
    resolved = resolve_profiles(profiles)
    assert len(resolved) == 1


def test_different_people_not_merged():
    profiles = [
        _profile("Rohit Kumar", employer="Swiggy"),
        _profile("Priya Nair", employer="Meesho"),
    ]
    resolved = resolve_profiles(profiles)
    assert len(resolved) == 2


def test_same_github_handle_merges():
    profiles = [
        _profile("Rohit Kumar", github="rohitkumar", adapter="github"),
        _profile("R. Kumar", github="rohitkumar", adapter="stackoverflow"),
    ]
    resolved = resolve_profiles(profiles)
    assert len(resolved) == 1
    assert "github" in resolved[0].source_names or "stackoverflow" in resolved[0].source_names


def test_skills_merged_across_sources():
    profiles = [
        _profile("Anjali Sharma", employer="Razorpay", github="anjali", skills=["python", "django"]),
        _profile("Anjali Sharma", employer="Razorpay", github="anjali", skills=["react", "typescript"]),
    ]
    resolved = resolve_profiles(profiles)
    assert len(resolved) == 1
    merged_skills = set(resolved[0].skills)
    assert "python" in merged_skills
    assert "react" in merged_skills


def test_name_similarity_exact():
    assert _name_similarity("Anjali Sharma", "Anjali Sharma") == 1.0


def test_name_similarity_partial():
    sim = _name_similarity("Anjali Sharma", "A. Sharma")
    assert sim > 0.0


def test_name_similarity_different():
    assert _name_similarity("Rohit Kumar", "Priya Nair") == 0.0


def test_single_profile_confidence_one():
    profiles = [_profile("Solo Dev")]
    resolved = resolve_profiles(profiles)
    assert resolved[0].confidence == 1.0


def test_empty_input():
    assert resolve_profiles([]) == []


def test_merge_confidence_handle_match():
    a = _profile("A", github="samehandle")
    b = _profile("B", github="samehandle")
    conf = _merge_confidence(a, b)
    assert conf >= 0.6


def test_merge_confidence_name_employer_match():
    a = _profile("Anjali Sharma", employer="Razorpay")
    b = _profile("Anjali Sharma", employer="Razorpay")
    conf = _merge_confidence(a, b)
    assert conf >= 0.85
