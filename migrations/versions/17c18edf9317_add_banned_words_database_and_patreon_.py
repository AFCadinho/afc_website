"""Add Banned Words database and patreon features in user and teams

Revision ID: 17c18edf9317
Revises: 37c2ef082ea1
Create Date: 2024-12-18 21:47:19.325819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17c18edf9317'
down_revision = '37c2ef082ea1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('banned_names',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Add `patreon_post` column with a default value for existing rows
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('patreon_post', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # Add `is_patreon` column to `users` (nullable, no conflicts)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_patreon', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_patreon')

    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_column('patreon_post')

    op.drop_table('banned_names')
    # ### end Alembic commands ###
