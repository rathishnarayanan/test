"""Suppression list enforcement."""
import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import SuppressionList


def _hash(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


async def is_suppressed(
    db: AsyncSession,
    workspace_id: str,
    email: str | None = None,
    phone: str | None = None,
) -> bool:
    email_hash = _hash(email)
    phone_hash = _hash(phone)

    stmt = select(SuppressionList).where(
        SuppressionList.workspace_id == workspace_id,
    )
    if email_hash:
        stmt = stmt.where(SuppressionList.email_hash == email_hash)
    elif phone_hash:
        stmt = stmt.where(SuppressionList.phone_hash == phone_hash)
    else:
        return False

    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def suppress(
    db: AsyncSession,
    workspace_id: str,
    email: str | None = None,
    phone: str | None = None,
    reason: str = "opt_out",
) -> None:
    entry = SuppressionList(
        workspace_id=workspace_id,
        email_hash=_hash(email),
        phone_hash=_hash(phone),
        reason=reason,
    )
    db.add(entry)
    await db.commit()
