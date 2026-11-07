"""DuckDuckGo search adapter — no API key required."""
from app.adapters.base import SourceAdapter, SearchQuery, RawProfile

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


class DuckDuckGoAdapter(SourceAdapter):
    async def search(self, query: SearchQuery) -> list[RawProfile]:
        if not DDGS_AVAILABLE:
            return []

        skill_str = " ".join(query.skills_must[:3])
        title_str = query.titles[0] if query.titles else ""
        location_str = query.location or ""
        q = f'{title_str} {skill_str} {location_str} site:linkedin.com OR site:github.com'.strip()

        results: list[RawProfile] = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(q, max_results=min(query.limit, 20)):
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    results.append(RawProfile(
                        adapter_name="duckduckgo",
                        source_url=url,
                        full_name=title.split(" - ")[0].split(" | ")[0][:100],
                        current_title=None,
                        current_employer=None,
                        location=None,
                        skills=query.skills_must,
                        profile_urls={"web": url},
                        raw_data={"title": title, "body": body, "url": url},
                    ))
        except Exception:
            pass

        return results
