"""Mock contact adapter — returns masked dummy contact info."""
import hashlib
from app.adapters.base import ContactAdapter, Person, ContactResult


def _masked_email(name: str) -> str:
    slug = name.lower().replace(" ", "")[:4]
    return f"{slug[0]}***@example.com"


def _masked_phone() -> str:
    return "+91 ****5678"


class MockContactAdapter(ContactAdapter):
    async def find_contact(self, person: Person) -> ContactResult:
        return ContactResult(
            emails=[{"value": _masked_email(person.full_name), "confidence": 0.85, "source": "mock", "cost": 0}],
            phones=[{"value": _masked_phone(), "confidence": 0.70, "source": "mock", "cost": 0}],
            adapter_name="mock",
            found=True,
        )

    async def verify_email(self, email: str) -> bool:
        return True

    async def verify_phone(self, phone: str) -> bool:
        return True
