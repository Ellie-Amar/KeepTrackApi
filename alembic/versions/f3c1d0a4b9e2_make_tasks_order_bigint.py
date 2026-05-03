"""make tasks.order bigint

Revision ID: f3c1d0a4b9e2
Revises: b804909ec2a4
Create Date: 2026-05-03 06:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f3c1d0a4b9e2"
down_revision: Union[str, None] = "b804909ec2a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tasks",
        "order",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.execute(
        'UPDATE tasks SET "order" = GREATEST(LEAST("order", 2147483647), -2147483648) '
        'WHERE "order" > 2147483647 OR "order" < -2147483648'
    )
    op.alter_column(
        "tasks",
        "order",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
