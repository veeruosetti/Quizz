"""Initial migration

Revision ID: ffb12eac5432
Revises: 
Create Date: 2025-03-17 10:10:39.906378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffb12eac5432'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('avatar', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_phone'), ['phone'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('quiz',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=False),
    sa.Column('duration', sa.Enum('ONE_MINUTE', 'TWO_MUNUTES', 'THREE_MINUTES', 'FOUR_MINUTES', 'FIVE_MINUTES', name='questiondurationenum'), nullable=False),
    sa.Column('status', sa.Enum('OPEN', 'FROZEN', name='quizstatusenum'), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('topic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('quiz_question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('option1', sa.Text(), nullable=False),
    sa.Column('option2', sa.Text(), nullable=False),
    sa.Column('option3', sa.Text(), nullable=False),
    sa.Column('option4', sa.Text(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quiz.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('quiz_question')
    op.drop_table('topic')
    op.drop_table('quiz')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_phone'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('subject')
    # ### end Alembic commands ###
