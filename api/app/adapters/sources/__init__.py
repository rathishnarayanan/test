from app.adapters.sources.mock import MockSourceAdapter
from app.adapters.sources.github import GitHubAdapter
from app.adapters.sources.stackoverflow import StackOverflowAdapter
from app.adapters.sources.duckduckgo import DuckDuckGoAdapter

__all__ = ["MockSourceAdapter", "GitHubAdapter", "StackOverflowAdapter", "DuckDuckGoAdapter"]
