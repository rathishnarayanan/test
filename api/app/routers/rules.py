"""Rule builder endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.rule import Rule
from app.models.candidate import Candidate
from app.models.score import Score
from app.models.compliance import AuditLog
from app.adapters.registry import registry

router = APIRouter(prefix="/api/jobs/{role_id}/rules", tags=["rules"])

DEMO_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


class CreateRuleRequest(BaseModel):
    natural_language: str


@router.post("")
async def create_rule(role_id: str, req: CreateRuleRequest, db: AsyncSession = Depends(get_db)):
    llm = registry.get_llm_adapter()

    parse_resp = await llm.complete("rule_parse", {"natural_language": req.natural_language, "role_id": role_id})
    preview_resp = await llm.complete("rule_preview", {"structured": parse_resp.result})

    rule = Rule(
        workspace_id=DEMO_WORKSPACE_ID,
        role_id=uuid.UUID(role_id),
        name=req.natural_language[:80],
        natural_language=req.natural_language,
        structured=parse_resp.result,
        plain_preview=preview_resp.result.get("plain_preview"),
        confirmed=False,
        active=False,
        created_by=DEMO_USER_ID,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return {
        "id": str(rule.id),
        "natural_language": rule.natural_language,
        "structured": rule.structured,
        "plain_preview": rule.plain_preview,
        "confirmed": rule.confirmed,
    }


@router.put("/{rule_id}/confirm")
async def confirm_rule(role_id: str, rule_id: str, db: AsyncSession = Depends(get_db)):
    rule = await db.get(Rule, uuid.UUID(rule_id))
    if not rule:
        raise HTTPException(404, "Rule not found")

    rule.confirmed = True
    rule.active = True

    audit = AuditLog(
        workspace_id=DEMO_WORKSPACE_ID,
        user_id=DEMO_USER_ID,
        action="rule_confirmed",
        entity_type="rule",
        entity_id=rule.id,
        detail={"natural_language": rule.natural_language, "structured": rule.structured},
    )
    db.add(audit)
    await db.commit()
    return {"id": rule_id, "confirmed": True, "active": True}


@router.get("")
async def list_rules(role_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Rule).where(Rule.role_id == uuid.UUID(role_id), Rule.workspace_id == DEMO_WORKSPACE_ID)
    )
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "natural_language": r.natural_language,
            "plain_preview": r.plain_preview,
            "confirmed": r.confirmed,
            "active": r.active,
        }
        for r in rules
    ]


@router.get("/dashboard")
async def role_dashboard(role_id: str, db: AsyncSession = Depends(get_db)):
    """Shortlisted candidates: those matching any active confirmed rule."""
    rules_result = await db.execute(
        select(Rule).where(Rule.role_id == uuid.UUID(role_id), Rule.active == True, Rule.confirmed == True)
    )
    active_rules = rules_result.scalars().all()

    shortlisted = []
    for rule in active_rules:
        structured = rule.structured or {}
        field = structured.get("field", "total_score")
        operator = structured.get("operator", "gte")
        value = float(structured.get("value", 0))

        stmt = (
            select(Candidate, Score)
            .join(Score, (Score.candidate_id == Candidate.id) & (Score.role_id == uuid.UUID(role_id)))
            .where(
                Candidate.workspace_id == DEMO_WORKSPACE_ID,
                Candidate.suppressed == False,
            )
        )
        result = await db.execute(stmt)
        rows = result.fetchall()

        for row in rows:
            score_val = row.Score.total_score if field == "total_score" else row.Score.total_score
            matched = (
                (operator == "gte" and score_val >= value) or
                (operator == "gt" and score_val > value) or
                (operator == "lte" and score_val <= value) or
                (operator == "lt" and score_val < value)
            )
            if matched:
                shortlisted.append({
                    "candidate_id": str(row.Candidate.id),
                    "full_name": row.Candidate.full_name,
                    "current_title": row.Candidate.current_title,
                    "total_score": row.Score.total_score,
                    "admitted_by_rule": rule.plain_preview or rule.natural_language,
                    "rule_id": str(rule.id),
                })

    seen = set()
    unique = [s for s in shortlisted if not (s["candidate_id"] in seen or seen.add(s["candidate_id"]))]
    return {"shortlisted": unique, "rule_count": len(active_rules)}
