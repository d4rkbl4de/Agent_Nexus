"""create meetings table

Revision ID: ab4c266252e1
Revises: 
Create Date: 2025-12-02 14:53:58.947346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = 'ab4c266252e1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
   
    op.create_table('meetings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('transcript', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_id'), 'meetings', ['id'], unique=False)
 


def downgrade() -> None:
    """Downgrade schema."""
  
    op.drop_index(op.f('ix_meetings_id'), table_name='meetings')
    op.drop_table('meetings')

