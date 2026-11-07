"""Adapter interfaces. Every external integration implements one of these."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchQuery:
    titles: list[str]
    skills_must: list[str]
    skills_nice: list[str]
    location: str | None
    exclusions: list[str]
    limit: int = 50


@dataclass
class RawProfile:
    adapter_name: str
    source_url: str | None
    full_name: str
    current_title: str | None
    current_employer: str | None
    location: str | None
    skills: list[str]
    profile_urls: dict[str, Any]
    raw_data: dict[str, Any]


@dataclass
class Person:
    full_name: str
    current_employer: str | None = None
    location: str | None = None
    profile_urls: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContactResult:
    emails: list[dict]   # [{value, confidence, source, cost}]
    phones: list[dict]   # [{value, confidence, source, cost}]
    adapter_name: str
    found: bool


@dataclass
class LLMResponse:
    prompt_name: str
    result: dict[str, Any]
    mock: bool = False


@dataclass
class OutreachMessage:
    candidate_id: str
    role_id: str
    workspace_id: str
    channel: str           # whatsapp, email
    template_name: str
    variables: dict[str, Any]
    to_number: str | None = None
    to_email: str | None = None


@dataclass
class SendResult:
    success: bool
    adapter_name: str
    message_id: str | None
    error: str | None = None


@dataclass
class CallRequest:
    candidate_id: str
    role_id: str
    workspace_id: str
    to_number: str
    call_type: str         # screening, interview
    questions: list[str]


@dataclass
class CallResult:
    success: bool
    adapter_name: str
    call_id: str | None
    transcript: str | None
    answers: list[dict]    # [{question, answer, score}]
    error: str | None = None


@dataclass
class EmbeddingResult:
    vector: list[float]
    mock: bool = False


class SourceAdapter(ABC):
    @abstractmethod
    async def search(self, query: SearchQuery) -> list[RawProfile]: ...


class ContactAdapter(ABC):
    @abstractmethod
    async def find_contact(self, person: Person) -> ContactResult: ...

    @abstractmethod
    async def verify_email(self, email: str) -> bool: ...

    @abstractmethod
    async def verify_phone(self, phone: str) -> bool: ...


class LLMAdapter(ABC):
    @abstractmethod
    async def complete(self, prompt_name: str, variables: dict) -> LLMResponse: ...


class OutreachAdapter(ABC):
    @abstractmethod
    async def send(self, message: OutreachMessage) -> SendResult: ...


class TelephonyAdapter(ABC):
    @abstractmethod
    async def place_call(self, call: CallRequest) -> CallResult: ...


class EmbeddingAdapter(ABC):
    @abstractmethod
    async def embed(self, text: str) -> EmbeddingResult: ...
