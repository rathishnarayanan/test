"""Mock telephony adapter — simulates AI phone screen."""
import uuid
from app.adapters.base import TelephonyAdapter, CallRequest, CallResult


class MockTelephonyAdapter(TelephonyAdapter):
    async def place_call(self, call: CallRequest) -> CallResult:
        call_id = f"mock_call_{uuid.uuid4().hex[:8]}"
        answers = [
            {"question": q, "answer": f"[Mock answer to: {q[:60]}]", "score": 0.8}
            for q in call.questions
        ]
        transcript = "\n".join(
            f"AI: {a['question']}\nCandidate: {a['answer']}" for a in answers
        )
        return CallResult(
            success=True,
            adapter_name="mock_telephony",
            call_id=call_id,
            transcript=transcript,
            answers=answers,
        )
