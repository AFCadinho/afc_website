"""Add archetype column to Teams model

Revision ID: a35125ee8f69
Revises: 6f5a42f9a5bf
Create Date: 2024-12-15 16:20:36.116466

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = 'a35125ee8f69'
down_revision = '6f5a42f9a5bf'
branch_labels = None
depends_on = None


def upgrade():
    # Create the ENUM type first
    archetype_enum = ENUM(
        'Hyper Offense', 'Bulky Offense', 'Balanced', 'Stall', 
        'Rain', 'Sun', 'Sand', 'Trick Room', 'Unknown', 
        name='archetype_enum'
    )
    archetype_enum.create(op.get_bind(), checkfirst=True)

    # Add the column with the ENUM type
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'archetype', 
            archetype_enum,
            server_default='Unknown',
            nullable=False
        ))


def downgrade():
    # Drop the column
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_column('archetype')

    # Drop the ENUM type
    archetype_enum = ENUM(
        'Hyper Offense', 'Bulky Offense', 'Balanced', 'Stall', 
        'Rain', 'Sun', 'Sand', 'Trick Room', 'Unknown', 
        name='archetype_enum'
    )
    archetype_enum.drop(op.get_bind(), checkfirst=True)
