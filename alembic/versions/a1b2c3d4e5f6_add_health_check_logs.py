"""add uptime_logs table

Revision ID: a1b2c3d4e5f6
Revises: d819f6705856
Create Date: 2026-03-19 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd819f6705856'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'uptime_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('called_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('uptime_logs')
