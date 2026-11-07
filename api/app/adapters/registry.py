"""Adapter registry — selects adapters based on environment config."""
from app.adapters.base import (
    SourceAdapter, ContactAdapter, LLMAdapter,
    OutreachAdapter, TelephonyAdapter, EmbeddingAdapter,
)
from app.adapters.sources import MockSourceAdapter, GitHubAdapter, StackOverflowAdapter, DuckDuckGoAdapter, DevToAdapter, NpmAdapter, GoogleCSEAdapter, JuiceboxAdapter
from app.adapters.contact import MockContactAdapter
from app.adapters.contact.juicebox import JuiceboxContactAdapter
from app.adapters.llm import MockLLMAdapter
from app.adapters.outreach import MockOutreachAdapter
from app.adapters.telephony import MockTelephonyAdapter
from app.adapters.interview import MockInterviewAdapter
from app.adapters.embedding import MockEmbeddingAdapter
from app.config import settings

_SOURCE_MAP: dict[str, type[SourceAdapter]] = {
    "mock": MockSourceAdapter,
    "github": GitHubAdapter,
    "stackoverflow": StackOverflowAdapter,
    "duckduckgo": DuckDuckGoAdapter,
    "devto": DevToAdapter,
    "npm": NpmAdapter,
    "google_cse": GoogleCSEAdapter,
    "juicebox": JuiceboxAdapter,
}


class AdapterRegistry:
    def get_source_adapters(self) -> list[SourceAdapter]:
        adapters = []
        for name in settings.source_adapter_list:
            cls = _SOURCE_MAP.get(name)
            if cls:
                adapters.append(cls())
        return adapters or [MockSourceAdapter()]

    def get_contact_adapter(self) -> ContactAdapter:
        if settings.contact_adapter == "juicebox" or (
            settings.contact_adapter == "auto" and settings.juicebox_api_key
        ):
            return JuiceboxContactAdapter()
        return MockContactAdapter()

    def get_llm_adapter(self) -> LLMAdapter:
        if settings.llm_adapter == "mock":
            return MockLLMAdapter()
        return MockLLMAdapter()

    def get_whatsapp_adapter(self) -> OutreachAdapter:
        if settings.outreach_whatsapp_adapter == "mock":
            return MockOutreachAdapter()
        return MockOutreachAdapter()

    def get_email_adapter(self) -> OutreachAdapter:
        if settings.outreach_email_adapter == "mock":
            return MockOutreachAdapter()
        return MockOutreachAdapter()

    def get_telephony_adapter(self) -> TelephonyAdapter:
        if settings.telephony_adapter == "mock":
            return MockTelephonyAdapter()
        return MockTelephonyAdapter()

    def get_interview_adapter(self) -> TelephonyAdapter:
        if settings.interview_adapter == "mock":
            return MockInterviewAdapter()
        return MockInterviewAdapter()

    def get_embedding_adapter(self) -> EmbeddingAdapter:
        if settings.embedding_adapter == "mock":
            return MockEmbeddingAdapter()
        return MockEmbeddingAdapter()


registry = AdapterRegistry()
