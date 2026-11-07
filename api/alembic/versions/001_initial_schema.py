"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-11-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions (pgcrypto, vector) must be created by a superuser before running this migration:
    #   sudo -u postgres psql -d sourcing -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
    #   sudo -u postgres psql -d sourcing -c "CREATE EXTENSION IF NOT EXISTS vector;"  # if pgvector installed


    op.create_table(
        "workspaces",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("settings", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("role", sa.String(50), server_default="recruiter"),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "platform_candidates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("current_title", sa.String(255)),
        sa.Column("current_employer", sa.String(255)),
        sa.Column("location", sa.String(255)),
        sa.Column("skills", ARRAY(sa.String), server_default="{}"),
        sa.Column("profile_urls", JSONB, server_default="{}"),
        sa.Column("raw_sources", JSONB, server_default="[]"),
        sa.Column("embedding", sa.Text),  # stored as text until pgvector type is confirmed
        sa.Column("source_names", ARRAY(sa.String), server_default="{}"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "candidates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("platform_candidate_id", UUID(as_uuid=True), sa.ForeignKey("platform_candidates.id")),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("current_title", sa.String(255)),
        sa.Column("current_employer", sa.String(255)),
        sa.Column("location", sa.String(255)),
        sa.Column("skills", ARRAY(sa.String), server_default="{}"),
        sa.Column("profile_urls", JSONB, server_default="{}"),
        sa.Column("email_masked", sa.String(255)),
        sa.Column("phone_masked", sa.String(50)),
        sa.Column("email_revealed", sa.String(255)),
        sa.Column("phone_revealed", sa.String(50)),
        sa.Column("source_names", ARRAY(sa.String), server_default="{}"),
        sa.Column("raw_sources", JSONB, server_default="[]"),
        sa.Column("embedding", sa.Text),
        sa.Column("suppressed", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "candidate_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("adapter_name", sa.String(50), nullable=False),
        sa.Column("source_url", sa.Text),
        sa.Column("raw_data", JSONB, server_default="{}"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("jd_text", sa.Text, nullable=False),
        sa.Column("search_spec", JSONB),
        sa.Column("rubric", JSONB),
        sa.Column("mode", sa.String(20), server_default="manual"),
        sa.Column("auto_threshold", sa.Float),
        sa.Column("status", sa.String(30), server_default="draft"),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "scores",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("total_score", sa.Float, server_default="0"),
        sa.Column("components", JSONB, server_default="{}"),
        sa.Column("preference_model_version", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "labels",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("label", sa.String(10), nullable=False),
        sa.Column("reason_tags", ARRAY(sa.String), server_default="{}"),
        sa.Column("batch_number", sa.Integer, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "preference_model_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("features", JSONB, server_default="{}"),
        sa.Column("yes_rate", sa.Float, server_default="0"),
        sa.Column("label_counts", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("natural_language", sa.Text, nullable=False),
        sa.Column("structured", JSONB, server_default="{}"),
        sa.Column("plain_preview", sa.Text),
        sa.Column("confirmed", sa.Boolean, server_default="false"),
        sa.Column("active", sa.Boolean, server_default="false"),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "outreach_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("candidate_id", UUID(as_uuid=True), sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("channel", sa.String(30)),
        sa.Column("direction", sa.String(10)),
        sa.Column("content", sa.Text),
        sa.Column("status", sa.String(30)),
        sa.Column("adapter_name", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "suppression_list",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("email_hash", sa.String(64)),
        sa.Column("phone_hash", sa.String(64)),
        sa.Column("reason", sa.String(50), server_default="opt_out"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("detail", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Indexes
    op.create_index("ix_candidates_workspace_suppressed", "candidates", ["workspace_id", "suppressed"])
    op.create_index("ix_scores_workspace_role_score", "scores", ["workspace_id", "role_id", "total_score"])
    op.create_index("ix_labels_workspace_role_batch", "labels", ["workspace_id", "role_id", "batch_number"])
    op.create_index("ix_outreach_workspace_role_candidate", "outreach_events", ["workspace_id", "role_id", "candidate_id"])
    op.create_index("ix_suppression_email", "suppression_list", ["workspace_id", "email_hash"])
    op.create_index("ix_suppression_phone", "suppression_list", ["workspace_id", "phone_hash"])
    op.create_index("ix_audit_workspace_created", "audit_log", ["workspace_id", "created_at"])


def downgrade() -> None:
    for table in [
        "audit_log", "suppression_list", "outreach_events", "rules",
        "preference_model_versions", "labels", "scores", "roles",
        "candidate_sources", "candidates", "platform_candidates",
        "users", "workspaces",
    ]:
        op.drop_table(table)
