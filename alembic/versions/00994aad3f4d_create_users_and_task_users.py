"""create users and tasks_users

Revision ID: 00994aad3f4d
Revises: 21e6c6d376c0
Create Date: 2025-10-28 21:38:59.069009

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "00994aad3f4d"
down_revision: Union[str, None] = "21e6c6d376c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    with op.batch_alter_table("tasks") as batch:
        batch.alter_column(
            "user_id",
            new_column_name="owner_id",
            existing_type=postgresql.UUID(as_uuid=True),
            existing_nullable=False,
        )
        batch.create_foreign_key(
            "fk_tasks_owner",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    op.create_table(
        "tasks_users",
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )

    op.execute(
        """
        INSERT INTO tasks_users (task_id, user_id)
        SELECT id AS task_id, owner_id AS user_id
        FROM tasks
        ON CONFLICT DO NOTHING
    """
    )


def downgrade():
    op.drop_table("tasks_users")
    with op.batch_alter_table("tasks") as batch:
        batch.drop_constraint("fk_tasks_owner", type_="foreignkey")
        batch.alter_column(
            "owner_id",
            new_column_name="user_id",
            existing_type=postgresql.UUID(as_uuid=True),
            existing_nullable=False,
        )

    op.drop_table("users")
