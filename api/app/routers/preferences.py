"""What I've learned — preference management endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.adapters.registry import registry

router = APIRouter(prefix="/api/jobs/{role_id}/preferences", tags=["preferences"])

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.get("")
async def get_preferences(role_id: str, db: AsyncSession = Depends(get_db)):
    """Generate plain-language preference summary from mock LLM."""
    llm = registry.get_llm_adapter()
    resp = await llm.complete("preferences_summary", {"role_id": role_id})
    return resp.result


class UpdatePreferenceRequest(BaseModel):
    text: str


@router.put("/{pref_id}")
async def update_preference(role_id: str, pref_id: str, req: UpdatePreferenceRequest):
    # In Phase 1 with mock, just echo back the update
    return {"id": pref_id, "text": req.text, "updated": True}


@router.delete("/{pref_id}")
async def remove_preference(role_id: str, pref_id: str):
    return {"id": pref_id, "removed": True}
