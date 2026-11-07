"""Calibration service — batch selection, re-ranking, preference model."""
from __future__ import annotations
import random
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.candidate import Candidate
from app.models.score import Score
from app.models.label import Label, PreferenceModelVersion
import uuid


BATCH_SIZE = 25
MIN_LABELS_FOR_COMPLETION = 15
YES_RATE_STABILITY_THRESHOLD = 0.05  # stop suggesting when rate changes < 5%


async def get_calibration_batch(
    db: AsyncSession,
    role_id: uuid.UUID,
    workspace_id: uuid.UUID,
    batch_number: int = 1,
) -> list[dict]:
    """Return next batch of diverse profiles for labelling."""
    # Get already-labelled candidate IDs
    labelled_stmt = select(Label.candidate_id).where(
        Label.role_id == role_id,
        Label.workspace_id == workspace_id,
    )
    labelled_result = await db.execute(labelled_stmt)
    labelled_ids = {row[0] for row in labelled_result.fetchall()}

    # Get scored, unsuppressed candidates not yet labelled
    stmt = (
        select(Candidate, Score)
        .join(Score, (Score.candidate_id == Candidate.id) & (Score.role_id == role_id))
        .where(
            Candidate.workspace_id == workspace_id,
            Candidate.suppressed == False,
            Candidate.id.notin_(labelled_ids) if labelled_ids else True,
        )
        .order_by(Score.total_score.desc())
    )
    result = await db.execute(stmt)
    rows = result.fetchall()

    if not rows:
        return []

    # Mix: top scorers + random exploration
    top = [r for r in rows[: BATCH_SIZE * 2]]
    if len(top) > BATCH_SIZE:
        # Take top 60% + random 40% for diversity
        n_top = int(BATCH_SIZE * 0.6)
        n_random = BATCH_SIZE - n_top
        selected_top = top[:n_top]
        rest = top[n_top:]
        selected_random = random.sample(rest, min(n_random, len(rest)))
        selected = selected_top + selected_random
        random.shuffle(selected)
    else:
        selected = top

    return [
        {
            "candidate": row.Candidate,
            "score": row.Score,
        }
        for row in selected[:BATCH_SIZE]
    ]


async def compute_yes_rate(db: AsyncSession, role_id: uuid.UUID, workspace_id: uuid.UUID) -> float:
    stmt = select(Label).where(Label.role_id == role_id, Label.workspace_id == workspace_id)
    result = await db.execute(stmt)
    labels = result.scalars().all()
    if not labels:
        return 0.0
    yes_count = sum(1 for l in labels if l.label == "yes")
    return yes_count / len(labels)


async def rerank_candidates(
    db: AsyncSession,
    role_id: uuid.UUID,
    workspace_id: uuid.UUID,
) -> None:
    """Re-rank by applying label signals as score adjustments."""
    stmt = select(Label).where(Label.role_id == role_id, Label.workspace_id == workspace_id)
    result = await db.execute(stmt)
    labels = result.scalars().all()

    if not labels:
        return

    yes_ids = {l.candidate_id for l in labels if l.label == "yes"}
    no_ids = {l.candidate_id for l in labels if l.label == "no"}
    maybe_ids = {l.candidate_id for l in labels if l.label == "maybe"}

    scores_stmt = select(Score).where(Score.role_id == role_id, Score.workspace_id == workspace_id)
    scores_result = await db.execute(scores_stmt)
    scores = scores_result.scalars().all()

    for score in scores:
        adjustment = 0.0
        if score.candidate_id in yes_ids:
            adjustment = 10.0
        elif score.candidate_id in no_ids:
            adjustment = -15.0
        elif score.candidate_id in maybe_ids:
            adjustment = 3.0

        score.total_score = max(0.0, min(100.0, score.total_score + adjustment))

    await db.commit()


async def check_cold_start(
    db: AsyncSession,
    role_id: uuid.UUID,
    workspace_id: uuid.UUID,
) -> dict:
    """Detect cold-start conditions."""
    stmt = select(Label).where(Label.role_id == role_id, Label.workspace_id == workspace_id)
    result = await db.execute(stmt)
    labels = result.scalars().all()

    if not labels:
        return {"cold_start": False}

    all_no = all(l.label == "no" for l in labels)
    too_few = len(labels) < 5

    if all_no:
        return {"cold_start": True, "reason": "all_no", "suggestion": "All profiles were rejected. Consider broadening the job description or relaxing must-have skills."}
    if too_few:
        return {"cold_start": True, "reason": "too_few", "suggestion": "Not enough candidates found. Try expanding the search location or adding more skill variants."}

    return {"cold_start": False}
