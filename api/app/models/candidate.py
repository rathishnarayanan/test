import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
from app.database import Base


class PlatformCandidate(Base):
    """Universal pool — platform-owned, all workspaces read-only."""
    __tablename__ = "platform_candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_title: Mapped[str | None] = mapped_column(String(255))
    current_employer: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    skills: Mapped[list] = mapped_column(ARRAY(String), default=list)
    profile_urls: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_sources: Mapped[list] = mapped_column(JSON, default=list)
    embedding: Mapped[list | None] = mapped_column(Vector(768), nullable=True)
    source_names: Mapped[list] = mapped_column(ARRAY(String), default=list)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Candidate(Base):
    """Client-specific deduplicated profiles."""
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    platform_candidate_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("platform_candidates.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_title: Mapped[str | None] = mapped_column(String(255))
    current_employer: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    skills: Mapped[list] = mapped_column(ARRAY(String), default=list)
    profile_urls: Mapped[dict] = mapped_column(JSON, default=dict)
    email_masked: Mapped[str | None] = mapped_column(String(255))
    phone_masked: Mapped[str | None] = mapped_column(String(50))
    email_revealed: Mapped[str | None] = mapped_column(String(255))  # encrypted at rest
    phone_revealed: Mapped[str | None] = mapped_column(String(50))   # encrypted at rest
    source_names: Mapped[list] = mapped_column(ARRAY(String), default=list)
    raw_sources: Mapped[list] = mapped_column(JSON, default=list)
    embedding: Mapped[list | None] = mapped_column(Vector(768), nullable=True)
    suppressed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class CandidateSource(Base):
    """One row per raw source record before deduplication."""
    __tablename__ = "candidate_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    adapter_name: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
