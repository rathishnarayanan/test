"""Entity resolution — merge raw profiles of the same person across sources."""
from __future__ import annotations
import re
from dataclasses import dataclass
from app.adapters.base import RawProfile


@dataclass
class ResolvedProfile:
    full_name: str
    current_title: str | None
    current_employer: str | None
    location: str | None
    skills: list[str]
    profile_urls: dict
    source_names: list[str]
    raw_sources: list[dict]
    confidence: float  # 0-1 merge confidence


def _normalise_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.lower().strip())


def _name_similarity(a: str, b: str) -> float:
    a, b = _normalise_name(a), _normalise_name(b)
    if a == b:
        return 1.0
    a_parts, b_parts = set(a.split()), set(b.split())
    if not a_parts or not b_parts:
        return 0.0
    overlap = len(a_parts & b_parts)
    return overlap / max(len(a_parts), len(b_parts))


def _employer_match(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return _normalise_name(a) == _normalise_name(b)


def _extract_handle(url: str | None) -> str | None:
    if not url:
        return None
    parts = [p for p in url.rstrip("/").split("/") if p]
    return parts[-1].lower() if parts else None


def _handle_match(a: dict, b: dict) -> bool:
    for key in ("github", "stackoverflow"):
        ha = _extract_handle(a.get(key))
        hb = _extract_handle(b.get(key))
        if ha and hb and ha == hb:
            return True
    return False


def _merge_confidence(a: RawProfile, b: RawProfile) -> float:
    name_sim = _name_similarity(a.full_name, b.full_name)
    employer_match = _employer_match(a.current_employer, b.current_employer)
    handle_match = _handle_match(a.profile_urls, b.profile_urls)

    if handle_match:
        return min(1.0, 0.6 + name_sim * 0.4)
    if name_sim >= 0.8 and employer_match:
        return 0.85
    if name_sim >= 0.9:
        return 0.75
    return 0.0


def resolve_profiles(raw_profiles: list[RawProfile], threshold: float = 0.6) -> list[ResolvedProfile]:
    """Merge raw profiles that likely represent the same person."""
    clusters: list[list[RawProfile]] = []

    for profile in raw_profiles:
        matched = False
        for cluster in clusters:
            representative = cluster[0]
            conf = _merge_confidence(representative, profile)
            if conf >= threshold:
                cluster.append(profile)
                matched = True
                break
        if not matched:
            clusters.append([profile])

    resolved = []
    for cluster in clusters:
        primary = cluster[0]
        merged_skills = list({s.lower() for p in cluster for s in p.skills})
        merged_urls: dict = {}
        for p in cluster:
            merged_urls.update(p.profile_urls)

        confidence = 1.0 if len(cluster) == 1 else _merge_confidence(cluster[0], cluster[1])

        resolved.append(ResolvedProfile(
            full_name=primary.full_name,
            current_title=next((p.current_title for p in cluster if p.current_title), None),
            current_employer=next((p.current_employer for p in cluster if p.current_employer), None),
            location=next((p.location for p in cluster if p.location), None),
            skills=merged_skills,
            profile_urls=merged_urls,
            source_names=list({p.adapter_name for p in cluster}),
            raw_sources=[p.raw_data for p in cluster],
            confidence=confidence,
        ))

    return resolved
