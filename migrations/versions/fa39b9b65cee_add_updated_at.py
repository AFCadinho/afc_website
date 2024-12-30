"""add updated at

Revision ID: fa39b9b65cee
Revises: c85202f31d58
Create Date: 2024-12-28 16:08:29.909859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa39b9b65cee'
down_revision = 'c85202f31d58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bans', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bans', schema=None) as batch_op:
        batch_op.drop_column('updated_at')

    # ### end Alembic commands ###