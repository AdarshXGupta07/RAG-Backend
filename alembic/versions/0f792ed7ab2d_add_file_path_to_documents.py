"""add_file_path_to_documents

Revision ID: 0f792ed7ab2d
Revises: c8469da21340
Create Date: 2026-06-21 11:31:34.521429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f792ed7ab2d'
down_revision: Union[str, Sequence[str], None] = 'c8469da21340'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'documents',
        sa.Column('file_path', sa.String(), nullable=True)
    )

def downgrade():
    op.drop_column('documents', 'file_path')
