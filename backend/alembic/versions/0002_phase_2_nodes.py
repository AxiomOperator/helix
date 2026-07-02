"""phase 2 node enrollment and agent connectivity

Revision ID: 0002_phase_2_nodes
Revises: 0001_phase_1_auth
Create Date: 2026-07-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_phase_2_nodes"
down_revision: Union[str, None] = "0001_phase_1_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("public_id", sa.Text(), nullable=False),
        sa.Column("machine_id", sa.Text(), nullable=False),
        sa.Column("hostname", sa.Text(), nullable=False),
        sa.Column("os_name", sa.Text()),
        sa.Column("kernel", sa.Text()),
        sa.Column("architecture", sa.Text()),
        sa.Column("online", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_nodes_public_id", "nodes", ["public_id"])
    op.create_unique_constraint("uq_nodes_machine_id", "nodes", ["machine_id"])

    op.create_table(
        "enrollment_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("public_id", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_enrollment_tokens_public_id", "enrollment_tokens", ["public_id"])
    op.create_unique_constraint("uq_enrollment_tokens_token_hash", "enrollment_tokens", ["token_hash"])

    op.create_table(
        "agent_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("node_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_agent_credentials_token_hash", "agent_credentials", ["token_hash"])


def downgrade() -> None:
    op.drop_table("agent_credentials")
    op.drop_table("enrollment_tokens")
    op.drop_table("nodes")
