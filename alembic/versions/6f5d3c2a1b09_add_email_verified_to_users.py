"""add email_verified to users

Revision ID: 6f5d3c2a1b09
Revises: f3c1d0a4b9e2
Create Date: 2026-05-03 23:58:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f5d3c2a1b09"
down_revision: Union[str, None] = "f3c1d0a4b9e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade():
    op.drop_column("users", "email_verified")
