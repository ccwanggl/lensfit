"""merge migration heads 002 and c53e30ed595b

Revision ID: 003
Revises: 002, c53e30ed595b
Create Date: 2026-06-12 16:00:00.000000

"""
# revision identifiers, used by Alembic.
revision = '003'
down_revision = ('002', 'c53e30ed595b')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge point for the 002 and c53e30ed595b branches.

    Both parent revisions already applied their schema changes; this revision
    exists only to unify the Alembic history into a single head.
    """
    pass


def downgrade() -> None:
    """No-op downgrade for merge point."""
    pass
