"""Juicebox (juicebox.ai) people-search adapter.

Juicebox aggregates LinkedIn, GitHub, Twitter, Crunchbase and others into
pre-enriched, deduplicated profiles. Masked contact info (email, phone)
ships with every search result at no extra credit cost.

Requires JUICEBOX_API_KEY in env.
When key is absent, returns [] silently (Phase 1 graceful no-op).
Phase 2: set JUICEBOX_API_KEY to activate real results.
"""
import httpx
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile
from app.config import settings

JUICEBOX_API = "https://api.juicebox.ai/v1"


class JuiceboxAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        if not settings.juicebox_api_key:
            return []

        # Build a structured search body. Juicebox accepts both NL and
        # structured filters; structured gives cleaner results.
        title_str = query.titles[0] if query.titles else ""
        skill_str = " ".join(query.skills_must[:5])
        nl_query = f"{title_str} {skill_str}".strip()

        body: dict = {
            "query": nl_query,
            "per_page": min(query.limit, 25),
            "page": 1,
        }
        if query.titles:
            body["filters"] = body.get("filters", {})
            body["filters"]["titles"] = query.titles[:5]
        if query.skills_must:
            body.setdefault("filters", {})
            body["filters"]["skills"] = query.skills_must[:10]
        if query.location:
            body.setdefault("filters", {})
            body["filters"]["location"] = query.location
        if query.exclusions:
            body.setdefault("filters", {})
            body["filters"]["exclude_companies"] = query.exclusions

        results: list[RawProfile] = []
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"{JUICEBOX_API}/people/search",
                    json=body,
                    headers={
                        "x-api-key": settings.juicebox_api_key,
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code != 200:
                    return results
                people = resp.json().get("people", [])

            for person in people[:query.limit]:
                profile_urls: dict = {}
                if person.get("linkedin_url"):
                    profile_urls["linkedin"] = person["linkedin_url"]
                if person.get("github_url"):
                    profile_urls["github"] = person["github_url"]
                if person.get("twitter_url"):
                    profile_urls["twitter"] = person["twitter_url"]

                results.append(RawProfile(
                    adapter_name="juicebox",
                    source_url=person.get("linkedin_url") or person.get("github_url"),
                    full_name=person.get("name", ""),
                    current_title=person.get("title"),
                    current_employer=person.get("company"),
                    location=person.get("location"),
                    skills=person.get("skills", []),
                    profile_urls=profile_urls,
                    # Store masked contacts in raw_data; ContactAdapter reads them on reveal.
                    raw_data={
                        "juicebox_id": person.get("id"),
                        "masked_email": person.get("masked_email"),
                        "masked_phone": person.get("masked_phone"),
                        **person,
                    },
                ))

        except Exception:
            pass

        return results
