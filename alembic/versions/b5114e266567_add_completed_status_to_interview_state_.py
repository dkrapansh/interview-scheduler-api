"""add completed status to interview state machine

Revision ID: b5114e266567
Revises: 998fa066b1cd
Create Date: 2026-06-05 00:14:24.319516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5114e266567'
down_revision: Union[str, Sequence[str], None] = '998fa066b1cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
