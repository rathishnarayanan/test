"""Stack Overflow public search adapter — no key required (300 req/day unauthenticated)."""
import httpx
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile
from app.config import settings

SO_API = "https://api.stackexchange.com/2.3"


class StackOverflowAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        tags = ";".join(query.skills_must[:5])
        params = {
            "order": "desc",
            "sort": "reputation",
            "tagged": tags,
            "site": "stackoverflow",
            "pagesize": min(query.limit, 25),
            "filter": "!9_bDE.CA_",
        }
        if settings.stackoverflow_key:
            params["key"] = settings.stackoverflow_key

        results: list[RawProfile] = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{SO_API}/users", params=params)
                if resp.status_code != 200:
                    return results
                users = resp.json().get("items", [])

            for user in users[:query.limit]:
                profile_url = user.get("link", "")
                results.append(RawProfile(
                    adapter_name="stackoverflow",
                    source_url=profile_url,
                    full_name=user.get("display_name", ""),
                    current_title=None,
                    current_employer=None,
                    location=user.get("location"),
                    skills=query.skills_must,
                    profile_urls={"stackoverflow": profile_url},
                    raw_data=user,
                ))
        except Exception:
            pass

        return results
