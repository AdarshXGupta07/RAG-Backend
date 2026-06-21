"""add_embedding_column_to_chunks

Revision ID: c8469da21340
Revises: e91124e970e5
Create Date: 2026-06-21 00:41:44.686187

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'c8469da21340'
down_revision: Union[str, Sequence[str], None] = 'e91124e970e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    op.add_column(
        'chunks',
        sa.Column('embedding', Vector(1024), nullable=True)
    )

def downgrade():
    op.drop_column('chunks', 'embedding')