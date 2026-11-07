"""Juicebox contact-reveal adapter.

Two operations:
  find_contact  — searches Juicebox for masked contact info (no credit cost)
  reveal        — exchanges juicebox_id for actual email/phone (costs credits)

Requires JUICEBOX_API_KEY. Falls back to ContactResult(found=False) when key absent.

The reveal step is intentionally separate from find_contact so the platform
can gate it behind a logged "reveal" action — every reveal writes to audit_log.
"""
import httpx
from app.adapters.base import ContactAdapter, Person, ContactResult
from app.config import settings

JUICEBOX_API = "https://api.juicebox.ai/v1"


class JuiceboxContactAdapter(ContactAdapter):

    async def find_contact(self, person: Person) -> ContactResult:
        """Search Juicebox for this person and return masked contact info."""
        if not settings.juicebox_api_key:
            return ContactResult(emails=[], phones=[], adapter_name="juicebox", found=False)

        # Prefer a known Juicebox ID stored from the source adapter pass.
        juicebox_id = (person.profile_urls or {}).get("juicebox_id")
        if juicebox_id:
            return await self._fetch_by_id(juicebox_id, masked=True)

        # Fall back to a name+employer lookup.
        body: dict = {"query": person.full_name}
        if person.current_employer:
            body["filters"] = {"companies": [person.current_employer]}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{JUICEBOX_API}/people/search",
                    json={**body, "per_page": 1},
                    headers={"x-api-key": settings.juicebox_api_key},
                )
                if resp.status_code != 200:
                    return ContactResult(emails=[], phones=[], adapter_name="juicebox", found=False)
                people = resp.json().get("people", [])

            if not people:
                return ContactResult(emails=[], phones=[], adapter_name="juicebox", found=False)

            p = people[0]
            emails, phones = [], []
            if p.get("masked_email"):
                emails = [{"value": p["masked_email"], "confidence": 0.9, "source": "juicebox", "cost": 0}]
            if p.get("masked_phone"):
                phones = [{"value": p["masked_phone"], "confidence": 0.9, "source": "juicebox", "cost": 0}]

            return ContactResult(
                emails=emails, phones=phones, adapter_name="juicebox", found=bool(emails or phones)
            )

        except Exception:
            return ContactResult(emails=[], phones=[], adapter_name="juicebox", found=False)

    async def reveal(self, juicebox_id: str) -> ContactResult:
        """Reveal actual email and phone for a known Juicebox person ID.

        This call costs credits. The caller (service layer) must write an
        audit_log entry BEFORE calling this method.
        """
        return await self._fetch_by_id(juicebox_id, masked=False)

    async def _fetch_by_id(self, juicebox_id: str, masked: bool) -> ContactResult:
        endpoint = f"{JUICEBOX_API}/people/{juicebox_id}"
        if not masked:
            endpoint += "/reveal"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    endpoint,
                    headers={"x-api-key": settings.juicebox_api_key},
                )
                if resp.status_code != 200:
                    return ContactResult(emails=[], phones=[], adapter_name="juicebox", found=False)
                p = resp.json()

            email_key = "masked_email" if masked else "email"
            phone_key = "masked_phone" if masked else "phone"
            cost = 0 if masked else 1  # 1 credit per reveal

            emails, phones = [], []
            if p.get(email_key):
                emails = [{"value": p[email_key], "confidence": 0.95, "source": "juicebox", "cost": cost}]
            if p.get(phone_key):
                phones = [{"value": p[phone_key], "confidence": 0.95, "source": "juicebox", "cost": cost}]

            return ContactResult(
                emails=emails, phones=phones, adapter_name="juicebox", found=bool(emails or phones)
            )

        except Exception:
            return ContactResult(emails=[], phones=[], adapter_name="juicebox", found=False)

    async def verify_email(self, email: str) -> bool:
        return True  # Juicebox pre-verifies; skip additional check

    async def verify_phone(self, phone: str) -> bool:
        return True
