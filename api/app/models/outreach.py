import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class OutreachEvent(Base):
    __tablename__ = "outreach_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # shortlist_notice, whatsapp_sent, email_sent, phone_attempted,
    # interview_started, reply_received, opt_out
    channel: Mapped[str | None] = mapped_column(String(30))  # whatsapp, email, phone, interview
    direction: Mapped[str | None] = mapped_column(String(10))  # outbound, inbound
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(30))  # sent, delivered, replied, failed, opted_out
    adapter_name: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
