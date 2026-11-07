"""Job (role) management endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.role import Role
from app.adapters.registry import registry

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


class CreateJobRequest(BaseModel):
    title: str
    jd_text: str


class UpdateSearchSpecRequest(BaseModel):
    titles: list[str]
    skills_must: list[str]
    skills_nice: list[str]
    location: str | None = None
    exclusions: list[str] = []


class UpdateRubricRequest(BaseModel):
    criteria: list[dict]


class UpdateModeRequest(BaseModel):
    mode: str  # manual or auto
    auto_threshold: float | None = None


@router.post("")
async def create_job(req: CreateJobRequest, db: AsyncSession = Depends(get_db)):
    role = Role(
        workspace_id=DEMO_WORKSPACE_ID,
        title=req.title,
        jd_text=req.jd_text,
        created_by=DEMO_USER_ID,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return {"id": str(role.id), "title": role.title, "status": role.status}


@router.post("/{role_id}/parse")
async def parse_jd(role_id: str, db: AsyncSession = Depends(get_db)):
    role = await db.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(404, "Role not found")

    llm = registry.get_llm_adapter()
    resp = await llm.complete("jd_parse", {"jd_text": role.jd_text})

    role.search_spec = resp.result
    await db.commit()
    return {"search_spec": resp.result, "mock": resp.mock}


@router.put("/{role_id}/search-spec")
async def update_search_spec(role_id: str, req: UpdateSearchSpecRequest, db: AsyncSession = Depends(get_db)):
    role = await db.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(404, "Role not found")
    role.search_spec = req.model_dump()
    await db.commit()
    return {"search_spec": role.search_spec}


@router.put("/{role_id}/rubric")
async def update_rubric(role_id: str, req: UpdateRubricRequest, db: AsyncSession = Depends(get_db)):
    role = await db.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(404, "Role not found")
    role.rubric = req.model_dump()
    await db.commit()
    return {"rubric": role.rubric}


@router.put("/{role_id}/mode")
async def update_mode(role_id: str, req: UpdateModeRequest, db: AsyncSession = Depends(get_db)):
    role = await db.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(404, "Role not found")
    role.mode = req.mode
    role.auto_threshold = req.auto_threshold
    await db.commit()
    return {"mode": role.mode, "auto_threshold": role.auto_threshold}


@router.post("/{role_id}/source")
async def trigger_sourcing(role_id: str, db: AsyncSession = Depends(get_db)):
    role = await db.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(404, "Role not found")
    if not role.search_spec:
        raise HTTPException(400, "Confirm search spec before sourcing")
    if not role.rubric:
        raise HTTPException(400, "Confirm rubric before sourcing")

    from app.workers.tasks import run_sourcing
    run_sourcing.delay(str(role.id), str(role.workspace_id))
    return {"status": "sourcing_started", "role_id": role_id}


@router.get("/{role_id}")
async def get_job(role_id: str, db: AsyncSession = Depends(get_db)):
    role = await db.get(Role, uuid.UUID(role_id))
    if not role:
        raise HTTPException(404, "Role not found")
    return {
        "id": str(role.id),
        "title": role.title,
        "status": role.status,
        "search_spec": role.search_spec,
        "rubric": role.rubric,
        "mode": role.mode,
        "auto_threshold": role.auto_threshold,
    }


@router.get("")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Role).where(Role.workspace_id == DEMO_WORKSPACE_ID).order_by(Role.created_at.desc())
    )
    roles = result.scalars().all()
    return [{"id": str(r.id), "title": r.title, "status": r.status} for r in roles]
