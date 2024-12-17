"""change acrhetype to string type

Revision ID: 37c2ef082ea1
Revises: a35125ee8f69
Create Date: 2024-12-15 16:47:36.699783

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '37c2ef082ea1'
down_revision = 'a35125ee8f69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.alter_column('archetype',
               existing_type=postgresql.ENUM('Hyper Offense', 'Bulky Offense', 'Balanced', 'Stall', 'Rain', 'Sun', 'Sand', 'Trick Room', 'Unknown', name='archetype_enum'),
               type_=sa.Text(),
               existing_nullable=False,
               existing_server_default=sa.text("'Unknown'::archetype_enum"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.alter_column('archetype',
               existing_type=sa.Text(),
               type_=postgresql.ENUM('Hyper Offense', 'Bulky Offense', 'Balanced', 'Stall', 'Rain', 'Sun', 'Sand', 'Trick Room', 'Unknown', name='archetype_enum'),
               existing_nullable=False,
               existing_server_default=sa.text("'Unknown'::archetype_enum"))

    # ### end Alembic commands ###