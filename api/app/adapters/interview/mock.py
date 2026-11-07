"""Mock AI technical interview adapter."""
import uuid
from app.adapters.base import TelephonyAdapter, CallRequest, CallResult


class MockInterviewAdapter(TelephonyAdapter):
    async def place_call(self, call: CallRequest) -> CallResult:
        call_id = f"mock_interview_{uuid.uuid4().hex[:8]}"
        answers = [
            {
                "question": q["question"] if isinstance(q, dict) else q,
                "answer": f"[Mock technical answer demonstrating knowledge of {q.get('skill', 'the topic') if isinstance(q, dict) else 'the topic'}]",
                "score": 0.75,
            }
            for q in call.questions
        ]
        transcript_lines = []
        for a in answers:
            transcript_lines.append(f"Interviewer: {a['question']}")
            transcript_lines.append(f"Candidate: {a['answer']}")
        transcript = "\n".join(transcript_lines)

        return CallResult(
            success=True,
            adapter_name="mock_interview",
            call_id=call_id,
            transcript=transcript,
            answers=answers,
        )
