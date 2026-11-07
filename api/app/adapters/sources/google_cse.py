"""Google Custom Search Engine adapter — X-Ray on LinkedIn/GitHub.

Requires GOOGLE_CSE_KEY and GOOGLE_CSE_CX in env.
When keys are absent, returns [] silently (Phase 1 graceful no-op).
100 queries/day free; $5 per 1,000 after.
"""
import httpx
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile
from app.config import settings

CSE_URL = "https://www.googleapis.com/customsearch/v1"


class GoogleCSEAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        if not settings.google_cse_key or not settings.google_cse_cx:
            return []

        skill_str = " ".join(query.skills_must[:3])
        title_str = query.titles[0] if query.titles else ""
        location_str = query.location or ""
        q = f"site:linkedin.com OR site:github.com {title_str} {skill_str} {location_str}".strip()

        results: list[RawProfile] = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    CSE_URL,
                    params={
                        "key": settings.google_cse_key,
                        "cx": settings.google_cse_cx,
                        "q": q,
                        "num": min(query.limit, 10),
                    },
                )
                if resp.status_code != 200:
                    return results
                items = resp.json().get("items", [])

            for item in items:
                url = item.get("link", "")
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                name = title.split(" - ")[0].split(" | ")[0][:100]

                profile_urls: dict = {"web": url}
                if "github.com" in url:
                    profile_urls["github"] = url
                elif "linkedin.com" in url:
                    profile_urls["linkedin"] = url

                results.append(RawProfile(
                    adapter_name="google_cse",
                    source_url=url,
                    full_name=name,
                    current_title=None,
                    current_employer=None,
                    location=None,
                    skills=query.skills_must,
                    profile_urls=profile_urls,
                    raw_data={"title": title, "snippet": snippet, "url": url},
                ))

        except Exception:
            pass

        return results
