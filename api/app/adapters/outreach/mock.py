"""Mock outreach adapter — simulates send + reply after a short delay."""
import uuid
from app.adapters.base import OutreachAdapter, OutreachMessage, SendResult

MOCK_REPLY_TEXTS = {
    "whatsapp": "YES, I'm interested. Please go ahead.",
    "email": "Thank you for reaching out. I'm interested in this opportunity.",
}


class MockOutreachAdapter(OutreachAdapter):
    async def send(self, message: OutreachMessage) -> SendResult:
        message_id = f"mock_{message.channel}_{uuid.uuid4().hex[:8]}"
        return SendResult(
            success=True,
            adapter_name=f"mock_{message.channel}",
            message_id=message_id,
        )

    async def simulate_reply(self, message: OutreachMessage) -> str:
        """Return a mock reply text — called by worker after escalation delay."""
        return MOCK_REPLY_TEXTS.get(message.channel, "Yes, interested.")
