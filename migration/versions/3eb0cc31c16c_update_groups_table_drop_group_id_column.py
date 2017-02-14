"""update groups table - drop group_id column

Revision ID: 3eb0cc31c16c
Revises: 7714db49dc7d
Create Date: 2017-02-14 12:29:41.429254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eb0cc31c16c'
down_revision = '7714db49dc7d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('group', 'group_id')


def downgrade():
    pass
