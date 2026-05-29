"""add index on slots recruiter_id

Revision ID: 998fa066b1cd
Revises: ee10689cdbe6
Create Date: 2026-05-29 23:54:51.431355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '998fa066b1cd'
down_revision: Union[str, Sequence[str], None] = 'ee10689cdbe6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index(
        'ix_slots_recruiter_id',
        'slots',
        ['recruiter_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_slots_recruiter_id', table_name='slots')
