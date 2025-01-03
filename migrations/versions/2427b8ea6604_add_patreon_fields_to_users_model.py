"""Add Patreon fields to Users model

Revision ID: 2427b8ea6604
Revises: e5e56132d474
Create Date: 2024-12-29 00:18:27.781587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2427b8ea6604'
down_revision = 'e5e56132d474'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_patreon_linked', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_patreon_linked')

    # ### end Alembic commands ###
