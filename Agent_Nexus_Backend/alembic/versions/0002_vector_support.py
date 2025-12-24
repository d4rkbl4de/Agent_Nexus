from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

revision = "0002_vector_support"
down_revision = "0001_init_core_tables"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "vector_memory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("agent_id", UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE")),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index(
        "ix_vector_memory_embedding",
        "vector_memory",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
    )

def downgrade():
    op.drop_index("ix_vector_memory_embedding", table_name="vector_memory")
    op.drop_table("vector_memory")
