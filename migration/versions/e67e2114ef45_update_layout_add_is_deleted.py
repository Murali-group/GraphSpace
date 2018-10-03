"""Update layout add is deleted

Revision ID: e67e2114ef45
Revises: bb9a45e2ee5e
Create Date: 2017-07-03 11:40:07.100839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e67e2114ef45'
down_revision = 'bb9a45e2ee5e'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_deleted column
    op.execute('ALTER TABLE "layout" ADD "is_deleted" BOOLEAN DEFAULT false')
    op.execute('UPDATE "layout" SET "is_deleted"=false')


def downgrade():
    # Drop table is_deleted
    op.execute('ALTER TABLE "layout" DROP COLUMN "is_deleted"')
