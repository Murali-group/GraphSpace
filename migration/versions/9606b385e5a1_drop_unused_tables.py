"""drop unused tables

Revision ID: 9606b385e5a1
Revises: 
Create Date: 2017-02-13 15:40:55.119204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9606b385e5a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('feature')
    op.drop_table('feedback')
    op.drop_table('task_code')
    op.drop_table('task')
    op.drop_table('layout_status')
    op.drop_table('old_layout_schema')


def downgrade():
    op.create_table('feature')
    op.create_table('feedback')
    op.create_table('task_code')
    op.create_table('task')
    op.create_table('layout_status')
    op.create_table('old_layout_schema')
