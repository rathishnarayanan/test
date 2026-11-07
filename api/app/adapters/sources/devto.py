"""dev.to public API adapter — no API key required."""
import httpx
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile

DEVTO_API = "https://dev.to/api"


class DevToAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        skill = query.skills_must[0] if query.skills_must else (query.titles[0] if query.titles else "")
        if not skill:
            return []

        results: list[RawProfile] = []
        seen_usernames: set[str] = set()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{DEVTO_API}/articles",
                    params={"tag": skill.lower().replace(" ", ""), "per_page": min(query.limit, 30)},
                )
                if resp.status_code != 200:
                    return results
                articles = resp.json()

            for article in articles:
                user = article.get("user", {})
                username = user.get("username", "")
                if not username or username in seen_usernames:
                    continue
                seen_usernames.add(username)

                name = user.get("name") or username
                github_username = user.get("github_username")
                tags = article.get("tag_list", [])

                profile_urls: dict = {"devto": f"https://dev.to/{username}"}
                if github_username:
                    profile_urls["github"] = f"https://github.com/{github_username}"

                results.append(RawProfile(
                    adapter_name="devto",
                    source_url=f"https://dev.to/{username}",
                    full_name=name,
                    current_title=None,
                    current_employer=None,
                    location=None,
                    skills=list({skill.lower()} | {t.lower() for t in tags}),
                    profile_urls=profile_urls,
                    raw_data={"username": username, "article_id": article.get("id"), "tags": tags},
                ))

                if len(results) >= query.limit:
                    break

        except Exception:
            pass

        return results
