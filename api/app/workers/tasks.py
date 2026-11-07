"""Celery tasks for sourcing, outreach, escalation, and interview."""
import asyncio
import uuid
from datetime import datetime, timedelta
from app.workers.celery_app import celery_app
from app.config import settings


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_sourcing(self, role_id: str, workspace_id: str):
    """Run sourcing pipeline for a role."""
    try:
        from app.database import AsyncSessionLocal
        from app.models.role import Role
        from app.models.candidate import Candidate, CandidateSource
        from app.models.score import Score
        from app.adapters.registry import registry
        from app.adapters.base import SearchQuery
        from app.services.entity_resolution import resolve_profiles
        from app.services.scoring import score_candidate, components_to_dict
        from sqlalchemy import select, update

        async def _source():
            async with AsyncSessionLocal() as db:
                role = await db.get(Role, uuid.UUID(role_id))
                if not role or not role.search_spec:
                    return

                await db.execute(
                    update(Role).where(Role.id == role.id).values(status="sourcing")
                )
                await db.commit()

                query = SearchQuery(
                    titles=role.search_spec.get("titles", []),
                    skills_must=role.search_spec.get("skills_must", []),
                    skills_nice=role.search_spec.get("skills_nice", []),
                    location=role.search_spec.get("location"),
                    exclusions=role.search_spec.get("exclusions", []),
                )

                all_raw = []
                for adapter in registry.get_source_adapters():
                    try:
                        profiles = await adapter.search(query)
                        all_raw.extend(profiles)
                    except Exception:
                        pass

                resolved = resolve_profiles(all_raw)

                for profile in resolved:
                    candidate = Candidate(
                        workspace_id=uuid.UUID(workspace_id),
                        full_name=profile.full_name,
                        current_title=profile.current_title,
                        current_employer=profile.current_employer,
                        location=profile.location,
                        skills=profile.skills,
                        profile_urls=profile.profile_urls,
                        source_names=profile.source_names,
                        raw_sources=profile.raw_sources,
                    )
                    db.add(candidate)
                    await db.flush()

                    for raw in profile.raw_sources:
                        src = CandidateSource(
                            candidate_id=candidate.id,
                            workspace_id=uuid.UUID(workspace_id),
                            adapter_name=raw.get("adapter_name", "unknown"),
                            source_url=profile.profile_urls.get("github") or profile.profile_urls.get("web"),
                            raw_data=raw,
                        )
                        db.add(src)

                    cs = score_candidate(
                        candidate_skills=profile.skills,
                        candidate_title=profile.current_title,
                        candidate_location=profile.location,
                        candidate_employer=profile.current_employer,
                        candidate_profile_urls=profile.profile_urls,
                        candidate_raw_sources=profile.raw_sources,
                        rubric=role.rubric or {},
                        search_spec=role.search_spec or {},
                    )
                    score = Score(
                        workspace_id=uuid.UUID(workspace_id),
                        role_id=role.id,
                        candidate_id=candidate.id,
                        total_score=cs.total_score,
                        components=components_to_dict(cs),
                    )
                    db.add(score)

                await db.execute(
                    update(Role).where(Role.id == role.id).values(status="calibrating")
                )
                await db.commit()

        _run(_source())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def send_outreach(self, candidate_id: str, role_id: str, workspace_id: str, channel: str):
    """Send outreach message via configured adapter."""
    try:
        from app.database import AsyncSessionLocal
        from app.models.outreach import OutreachEvent
        from app.adapters.registry import registry
        from app.adapters.base import OutreachMessage

        async def _send():
            async with AsyncSessionLocal() as db:
                msg = OutreachMessage(
                    candidate_id=candidate_id,
                    role_id=role_id,
                    workspace_id=workspace_id,
                    channel=channel,
                    template_name="default",
                    variables={},
                )
                adapter = registry.get_whatsapp_adapter() if channel == "whatsapp" else registry.get_email_adapter()
                result = await adapter.send(msg)

                event = OutreachEvent(
                    workspace_id=uuid.UUID(workspace_id),
                    role_id=uuid.UUID(role_id),
                    candidate_id=uuid.UUID(candidate_id),
                    event_type=f"{channel}_sent",
                    channel=channel,
                    direction="outbound",
                    content=f"[Mock {channel} sent]",
                    status="sent" if result.success else "failed",
                    adapter_name=result.adapter_name,
                )
                db.add(event)
                await db.commit()

        _run(_send())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def check_outreach_escalations():
    """Check for no-reply outreach and escalate to next channel."""
    from app.database import AsyncSessionLocal
    from app.models.outreach import OutreachEvent
    from sqlalchemy import select

    async def _check():
        async with AsyncSessionLocal() as db:
            cutoff = datetime.utcnow() - timedelta(hours=settings.outreach_escalation_hours)
            stmt = select(OutreachEvent).where(
                OutreachEvent.event_type.in_(["whatsapp_sent", "email_sent"]),
                OutreachEvent.status == "sent",
                OutreachEvent.created_at < cutoff,
            )
            result = await db.execute(stmt)
            events = result.scalars().all()

            for event in events:
                if event.channel == "whatsapp":
                    send_outreach.delay(
                        str(event.candidate_id), str(event.role_id), str(event.workspace_id), "email"
                    )
                elif event.channel == "email":
                    place_phone_screen.delay(
                        str(event.candidate_id), str(event.role_id), str(event.workspace_id)
                    )

    _run(_check())


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def place_phone_screen(self, candidate_id: str, role_id: str, workspace_id: str):
    """Place AI phone screening call."""
    try:
        from app.database import AsyncSessionLocal
        from app.models.outreach import OutreachEvent
        from app.adapters.registry import registry
        from app.adapters.base import CallRequest

        async def _call():
            async with AsyncSessionLocal() as db:
                req = CallRequest(
                    candidate_id=candidate_id,
                    role_id=role_id,
                    workspace_id=workspace_id,
                    to_number="+910000000000",
                    call_type="screening",
                    questions=[
                        "Can you describe your relevant experience?",
                        "What is your current notice period?",
                        "Are you open to the work location?",
                    ],
                )
                result = await registry.get_telephony_adapter().place_call(req)

                event = OutreachEvent(
                    workspace_id=uuid.UUID(workspace_id),
                    role_id=uuid.UUID(role_id),
                    candidate_id=uuid.UUID(candidate_id),
                    event_type="phone_attempted",
                    channel="phone",
                    direction="outbound",
                    content=result.transcript,
                    status="sent" if result.success else "failed",
                    adapter_name=result.adapter_name,
                )
                db.add(event)
                await db.commit()

        _run(_call())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def run_technical_interview(self, candidate_id: str, role_id: str, workspace_id: str):
    """Run AI technical interview — only after screening answers received."""
    try:
        from app.database import AsyncSessionLocal
        from app.models.outreach import OutreachEvent
        from app.adapters.registry import registry
        from app.adapters.base import CallRequest
        from app.adapters.llm.mock import MockLLMAdapter

        async def _interview():
            async with AsyncSessionLocal() as db:
                llm = MockLLMAdapter()
                q_resp = await llm.complete("interview_questions", {})
                questions = q_resp.result.get("questions", [])

                req = CallRequest(
                    candidate_id=candidate_id,
                    role_id=role_id,
                    workspace_id=workspace_id,
                    to_number="+910000000000",
                    call_type="interview",
                    questions=questions,
                )
                result = await registry.get_interview_adapter().place_call(req)

                event = OutreachEvent(
                    workspace_id=uuid.UUID(workspace_id),
                    role_id=uuid.UUID(role_id),
                    candidate_id=uuid.UUID(candidate_id),
                    event_type="interview_started",
                    channel="interview",
                    direction="outbound",
                    content=result.transcript,
                    status="sent" if result.success else "failed",
                    adapter_name=result.adapter_name,
                )
                db.add(event)
                await db.commit()

        _run(_interview())
    except Exception as exc:
        raise self.retry(exc=exc)
