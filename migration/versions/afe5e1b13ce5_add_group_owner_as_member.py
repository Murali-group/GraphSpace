"""add group owner as member

Revision ID: afe5e1b13ce5
Revises: 1a2e1771d68e
Create Date: 2017-02-15 12:05:35.480896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afe5e1b13ce5'
down_revision = '1a2e1771d68e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DELETE FROM group_to_user AS g2u USING "group" AS g, "user" AS u WHERE (g2u.group_id = g.id) AND  (g2u.user_id = u.id)  AND g.owner_email = u.email;')
    op.execute('INSERT INTO group_to_user (SELECT "group".id, "user".id FROM "group", "user" WHERE "group".owner_email = "user".email);')
    pass


def downgrade():
    op.execute('DELETE FROM group_to_user AS g2u USING "group" AS g, "user" AS u WHERE (g2u.group_id = g.id) AND  (g2u.user_id = u.id)  AND g.owner_email = u.email;')
    pass