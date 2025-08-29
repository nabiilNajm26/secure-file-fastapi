"""add verification tokens table

Revision ID: add_verification_tokens
Revises: 
Create Date: 2024-08-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_verification_tokens'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create verification_tokens table
    op.create_table('verification_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_type', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_tokens_token'), 'verification_tokens', ['token'], unique=True)


def downgrade() -> None:
    # Drop verification_tokens table
    op.drop_index(op.f('ix_verification_tokens_token'), table_name='verification_tokens')
    op.drop_table('verification_tokens')