from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "0003_agent_memory"
down_revision = "0002_vector_support"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "agent_memory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("agent_id", UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE")),
        sa.Column("memory_type", sa.String(64), nullable=False),
        sa.Column("content", sa.JSON, nullable=False),
        sa.Column("importance", sa.Float, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index(
        "ix_agent_memory_agent_id",
        "agent_memory",
        ["agent_id"],
    )

def downgrade():
    op.drop_index("ix_agent_memory_agent_id", table_name="agent_memory")
    op.drop_table("agent_memory")
