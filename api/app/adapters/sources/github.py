"""GitHub public search adapter — no API key required (60 req/hour unauthenticated)."""
import httpx
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile
from app.config import settings

GITHUB_API = "https://api.github.com"


class GitHubAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        skill_query = " ".join(query.skills_must[:3])
        title_query = " OR ".join(f'"{t}"' for t in query.titles[:2])
        q = f"{skill_query} {title_query}".strip() or " ".join(query.skills_must)

        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"

        results: list[RawProfile] = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{GITHUB_API}/search/users",
                    params={"q": q, "per_page": min(query.limit, 30)},
                    headers=headers,
                )
                if resp.status_code != 200:
                    return results
                users = resp.json().get("items", [])

            for user in users[:query.limit]:
                profile_url = user.get("html_url", "")
                results.append(RawProfile(
                    adapter_name="github",
                    source_url=profile_url,
                    full_name=user.get("login", ""),
                    current_title=None,
                    current_employer=None,
                    location=None,
                    skills=[],
                    profile_urls={"github": profile_url},
                    raw_data=user,
                ))
        except Exception:
            pass

        return results
