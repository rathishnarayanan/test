"""npm registry adapter — no API key required."""
import httpx
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile

NPM_REGISTRY = "https://registry.npmjs.org"


class NpmAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        skill = query.skills_must[0] if query.skills_must else (query.titles[0] if query.titles else "")
        if not skill:
            return []

        results: list[RawProfile] = []
        seen_usernames: set[str] = set()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{NPM_REGISTRY}/-/v1/search",
                    params={"text": skill, "size": 25},
                )
                if resp.status_code != 200:
                    return results
                data = resp.json()

            for obj in data.get("objects", []):
                pkg = obj.get("package", {})
                for maintainer in pkg.get("maintainers", []):
                    username = maintainer.get("username") or maintainer.get("name", "")
                    if not username or username in seen_usernames:
                        continue
                    seen_usernames.add(username)

                    results.append(RawProfile(
                        adapter_name="npm",
                        source_url=f"https://www.npmjs.com/~{username}",
                        full_name=username,
                        current_title=None,
                        current_employer=None,
                        location=None,
                        skills=[skill.lower()],
                        profile_urls={"npm": f"https://www.npmjs.com/~{username}"},
                        raw_data={"username": username, "package": pkg.get("name"), "email": maintainer.get("email")},
                    ))

                    if len(results) >= query.limit:
                        break
                if len(results) >= query.limit:
                    break

        except Exception:
            pass

        return results
