"""Mock LLM adapter — returns structured dummy responses per prompt name."""
from app.adapters.base import LLMAdapter, LLMResponse

MOCK_RESPONSES: dict[str, dict] = {
    "jd_parse": {
        "titles": ["Software Engineer", "Backend Engineer", "Python Developer"],
        "skills_must": ["python", "postgresql", "docker"],
        "skills_nice": ["fastapi", "redis", "kubernetes", "aws"],
        "location": None,
        "exclusions": [],
    },
    "rule_parse": {
        "field": "total_score",
        "operator": "gte",
        "value": 75,
    },
    "rule_preview": {
        "plain_preview": "Candidates with a resume score of at least 75 are shortlisted.",
    },
    "screening_questions": {
        "questions": [
            "Can you describe your experience with Python and backend development?",
            "What databases have you worked with professionally?",
            "Are you open to the work location and schedule mentioned in the role?",
            "What is your current notice period?",
        ]
    },
    "interview_questions": {
        "questions": [
            {"skill": "python", "question": "Explain the difference between asyncio tasks and threads in Python."},
            {"skill": "postgresql", "question": "How would you optimise a slow query on a 10M-row table?"},
            {"skill": "docker", "question": "Walk me through how you would set up a multi-stage Docker build."},
        ]
    },
    "outreach_whatsapp": {
        "message": "Hi {candidate_name}, your profile has been shortlisted for the {role_title} role at {company}. We'd love to learn more about you. Are you open to a quick conversation? Reply YES to proceed or NO to opt out.",
    },
    "outreach_email": {
        "subject": "Your profile for {role_title} at {company}",
        "body": "Dear {candidate_name},\n\nWe reviewed your profile and believe you could be a great fit for the {role_title} role.\n\nWould you be open to a brief screening call?\n\nReply to this email or click below to opt out.\n\nBest regards,\nThe Recruiting Team",
    },
    "profile_summary": {
        "summary": "Experienced engineer with strong backend skills and relevant domain experience.",
        "highlights": ["Strong Python background", "PostgreSQL experience", "Containerisation skills"],
    },
    "preferences_summary": {
        "preferences": [
            {"id": "pref_1", "text": "Prefers candidates with active GitHub profiles"},
            {"id": "pref_2", "text": "Favours engineers at product companies over IT services"},
            {"id": "pref_3", "text": "Values recent activity in the last 12 months"},
        ]
    },
}


class MockLLMAdapter(LLMAdapter):
    async def complete(self, prompt_name: str, variables: dict) -> LLMResponse:
        result = MOCK_RESPONSES.get(prompt_name, {"mock": True, "prompt_name": prompt_name})
        return LLMResponse(prompt_name=prompt_name, result=result, mock=True)
