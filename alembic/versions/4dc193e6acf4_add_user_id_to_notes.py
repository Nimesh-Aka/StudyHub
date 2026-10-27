"""add user_id to notes

Revision ID: 4dc193e6acf4
Revises: cc17b2471034
Create Date: 2026-10-27 20:09:25.539250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '4dc193e6acf4'
down_revision: Union[str, Sequence[str], None] = 'cc17b2471034'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Add user_id only if it is missing.
    columns = [
        column["name"]
        for column in inspector.get_columns("notes")
    ]

    if "user_id" not in columns:
        op.add_column(
            "notes",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )

    # Add the foreign key only if it is missing.
    inspector = inspect(bind)
    foreign_keys = inspector.get_foreign_keys("notes")

    has_user_fk = any(
        fk.get("constrained_columns") == ["user_id"]
        and fk.get("referred_table") == "users"
        and fk.get("referred_columns") == ["id"]
        for fk in foreign_keys
    )

    if not has_user_fk:
        op.create_foreign_key(
            "fk_notes_user_id",
            "notes",
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    pass
