"""Audit log endpoints."""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.compliance import AuditLog

router = APIRouter(prefix="/api/audit", tags=["audit"])

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.get("")
async def list_audit_log(
    action: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(AuditLog)
        .where(AuditLog.workspace_id == DEMO_WORKSPACE_ID)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    if action:
        stmt = stmt.where(AuditLog.action == action)

    result = await db.execute(stmt)
    entries = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "action": e.action,
            "entity_type": e.entity_type,
            "entity_id": str(e.entity_id) if e.entity_id else None,
            "detail": e.detail,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]
