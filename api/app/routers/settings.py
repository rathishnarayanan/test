"""Workspace settings endpoints."""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models.workspace import Workspace
from app.config import settings as app_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

DEFAULT_SETTINGS = {
    "retention_days": 90,
    "contact_reveal_enabled": False,
    "source_adapters": ["mock", "github", "stackoverflow", "duckduckgo", "devto", "npm"],
}


class SettingsUpdate(BaseModel):
    retention_days: int | None = None
    contact_reveal_enabled: bool | None = None
    source_adapters: List[str] | None = None


async def _get_workspace(db: AsyncSession) -> Workspace | None:
    result = await db.execute(
        select(Workspace).where(Workspace.id == DEMO_WORKSPACE_ID)
    )
    return result.scalar_one_or_none()


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db)):
    ws = await _get_workspace(db)
    stored = ws.settings if ws else {}
    merged = {**DEFAULT_SETTINGS, **stored}
    return {
        "retention_days": merged.get("retention_days", 90),
        "contact_reveal_enabled": merged.get("contact_reveal_enabled", False),
        "source_adapters": merged.get("source_adapters", DEFAULT_SETTINGS["source_adapters"]),
        "api_keys": {
            "github_token": app_settings.github_token is not None,
            "juicebox_api_key": app_settings.juicebox_api_key is not None,
            "google_cse": app_settings.google_cse_key is not None and app_settings.google_cse_cx is not None,
            "stackoverflow_key": app_settings.stackoverflow_key is not None,
        },
    }


@router.put("")
async def update_settings(body: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    ws = await _get_workspace(db)
    if not ws:
        return {"error": "workspace not found"}

    current = dict(ws.settings or {})
    if body.retention_days is not None:
        current["retention_days"] = body.retention_days
    if body.contact_reveal_enabled is not None:
        current["contact_reveal_enabled"] = body.contact_reveal_enabled
    if body.source_adapters is not None:
        current["source_adapters"] = body.source_adapters

    ws.settings = current
    await db.commit()

    merged = {**DEFAULT_SETTINGS, **current}
    return {
        "retention_days": merged.get("retention_days", 90),
        "contact_reveal_enabled": merged.get("contact_reveal_enabled", False),
        "source_adapters": merged.get("source_adapters", DEFAULT_SETTINGS["source_adapters"]),
    }
