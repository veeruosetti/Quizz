"""add extra fields of topic

Revision ID: 4f6ad5592a1a
Revises: a31425d299b5
Create Date: 2025-03-08 12:25:25.497899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f6ad5592a1a'
down_revision = 'a31425d299b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topic', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('difficulty_level', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('topic', schema=None) as batch_op:
        batch_op.drop_column('is_active')
        batch_op.drop_column('difficulty_level')
        batch_op.drop_column('duration')

    # ### end Alembic commands ###
