"""Candidate pool, scoring, and calibration endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import csv
import io
from app.database import get_db
from app.models.candidate import Candidate
from app.models.score import Score
from app.models.label import Label
from app.models.outreach import OutreachEvent
from app.models.compliance import AuditLog
from app.services.calibration import (
    get_calibration_batch, compute_yes_rate, rerank_candidates, check_cold_start
)

router = APIRouter(prefix="/api/jobs/{role_id}", tags=["candidates"])

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


@router.get("/candidates")
async def list_candidates(
    role_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    min_score: float = Query(0.0),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    stmt = (
        select(Candidate, Score)
        .join(Score, (Score.candidate_id == Candidate.id) & (Score.role_id == uuid.UUID(role_id)))
        .where(
            Candidate.workspace_id == DEMO_WORKSPACE_ID,
            Candidate.suppressed == False,
            Score.total_score >= min_score,
        )
        .order_by(Score.total_score.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    rows = result.fetchall()

    return [
        {
            "id": str(r.Candidate.id),
            "full_name": r.Candidate.full_name,
            "current_title": r.Candidate.current_title,
            "current_employer": r.Candidate.current_employer,
            "location": r.Candidate.location,
            "skills": r.Candidate.skills,
            "total_score": r.Score.total_score,
            "source_names": r.Candidate.source_names,
            "profile_urls": r.Candidate.profile_urls,
        }
        for r in rows
    ]


@router.get("/candidates/{candidate_id}/score")
async def get_score(role_id: str, candidate_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Score).where(
        Score.role_id == uuid.UUID(role_id),
        Score.candidate_id == uuid.UUID(candidate_id),
        Score.workspace_id == DEMO_WORKSPACE_ID,
    )
    result = await db.execute(stmt)
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(404, "Score not found")
    return {
        "candidate_id": candidate_id,
        "total_score": score.total_score,
        "components": score.components,
        "preference_model_version": score.preference_model_version,
    }


@router.get("/candidates/export")
async def export_candidates(role_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Candidate, Score)
        .join(Score, (Score.candidate_id == Candidate.id) & (Score.role_id == uuid.UUID(role_id)))
        .where(Candidate.workspace_id == DEMO_WORKSPACE_ID, Candidate.suppressed == False)
        .order_by(Score.total_score.desc())
    )
    result = await db.execute(stmt)
    rows = result.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Title", "Employer", "Location", "Skills", "Score", "Sources"])
    for r in rows:
        writer.writerow([
            r.Candidate.full_name,
            r.Candidate.current_title or "",
            r.Candidate.current_employer or "",
            r.Candidate.location or "",
            ", ".join(r.Candidate.skills),
            r.Score.total_score,
            ", ".join(r.Candidate.source_names),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=candidates_{role_id}.csv"},
    )


# ── Calibration ───────────────────────────────────────────────────────────────

@router.get("/calibration/batch")
async def get_batch(role_id: str, batch_number: int = Query(1), db: AsyncSession = Depends(get_db)):
    batch = await get_calibration_batch(db, uuid.UUID(role_id), DEMO_WORKSPACE_ID, batch_number)
    cold_start = await check_cold_start(db, uuid.UUID(role_id), DEMO_WORKSPACE_ID)
    yes_rate = await compute_yes_rate(db, uuid.UUID(role_id), DEMO_WORKSPACE_ID)

    return {
        "batch": [
            {
                "candidate_id": str(item["candidate"].id),
                "full_name": item["candidate"].full_name,
                "current_title": item["candidate"].current_title,
                "current_employer": item["candidate"].current_employer,
                "location": item["candidate"].location,
                "skills": item["candidate"].skills,
                "total_score": item["score"].total_score,
                "components": item["score"].components,
                "profile_urls": item["candidate"].profile_urls,
            }
            for item in batch
        ],
        "yes_rate": yes_rate,
        "cold_start": cold_start,
    }


class LabelRequest(BaseModel):
    candidate_id: str
    label: str  # yes, no, maybe
    reason_tags: list[str] = []
    batch_number: int = 1


@router.post("/calibration/label")
async def apply_label(role_id: str, req: LabelRequest, db: AsyncSession = Depends(get_db)):
    if req.label not in ("yes", "no", "maybe"):
        raise HTTPException(400, "label must be yes, no, or maybe")

    label = Label(
        workspace_id=DEMO_WORKSPACE_ID,
        role_id=uuid.UUID(role_id),
        candidate_id=uuid.UUID(req.candidate_id),
        user_id=DEMO_USER_ID,
        label=req.label,
        reason_tags=req.reason_tags,
        batch_number=req.batch_number,
    )
    db.add(label)

    audit = AuditLog(
        workspace_id=DEMO_WORKSPACE_ID,
        user_id=DEMO_USER_ID,
        action="label_applied",
        entity_type="candidate",
        entity_id=uuid.UUID(req.candidate_id),
        detail={"label": req.label, "reason_tags": req.reason_tags, "role_id": role_id},
    )
    db.add(audit)
    await db.commit()

    yes_rate = await compute_yes_rate(db, uuid.UUID(role_id), DEMO_WORKSPACE_ID)
    return {"label": req.label, "yes_rate": yes_rate}


@router.post("/calibration/rerank")
async def rerank(role_id: str, db: AsyncSession = Depends(get_db)):
    await rerank_candidates(db, uuid.UUID(role_id), DEMO_WORKSPACE_ID)
    yes_rate = await compute_yes_rate(db, uuid.UUID(role_id), DEMO_WORKSPACE_ID)
    return {"status": "reranked", "yes_rate": yes_rate}


# ── Outreach timeline ─────────────────────────────────────────────────────────

@router.get("/candidates/{candidate_id}/timeline")
async def get_timeline(role_id: str, candidate_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(OutreachEvent).where(
        OutreachEvent.role_id == uuid.UUID(role_id),
        OutreachEvent.candidate_id == uuid.UUID(candidate_id),
        OutreachEvent.workspace_id == DEMO_WORKSPACE_ID,
    ).order_by(OutreachEvent.created_at)
    result = await db.execute(stmt)
    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "channel": e.channel,
            "direction": e.direction,
            "content": e.content,
            "status": e.status,
            "adapter_name": e.adapter_name,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.post("/candidates/{candidate_id}/outreach")
async def trigger_outreach(role_id: str, candidate_id: str, db: AsyncSession = Depends(get_db)):
    from app.workers.tasks import send_outreach
    send_outreach.delay(candidate_id, role_id, str(DEMO_WORKSPACE_ID), "whatsapp")
    return {"status": "outreach_queued", "channel": "whatsapp"}


@router.post("/candidates/{candidate_id}/move-to-interview")
async def move_to_interview(role_id: str, candidate_id: str, db: AsyncSession = Depends(get_db)):
    """Recruiter action — move candidate to human interview stage."""
    event = OutreachEvent(
        workspace_id=DEMO_WORKSPACE_ID,
        role_id=uuid.UUID(role_id),
        candidate_id=uuid.UUID(candidate_id),
        event_type="moved_to_human_interview",
        channel=None,
        direction=None,
        content="Recruiter moved candidate to human interview stage",
        status="done",
        adapter_name=None,
    )
    db.add(event)
    audit = AuditLog(
        workspace_id=DEMO_WORKSPACE_ID,
        user_id=DEMO_USER_ID,
        action="moved_to_human_interview",
        entity_type="candidate",
        entity_id=uuid.UUID(candidate_id),
        detail={"role_id": role_id},
    )
    db.add(audit)
    await db.commit()
    return {"status": "moved_to_human_interview"}
