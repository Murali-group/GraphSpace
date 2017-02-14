"""update graph table - add default layout fkey

Revision ID: 1a2e1771d68e
Revises: 3eb0cc31c16c
Create Date: 2017-02-14 12:31:11.998702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2e1771d68e'
down_revision = '3eb0cc31c16c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('UPDATE graph SET default_layout_id=NULL WHERE NOT EXISTS (SELECT 1 FROM "layout" WHERE (graph.default_layout_id = "layout".id))')
    op.execute('ALTER TABLE "graph" ADD CONSTRAINT graph_default_layout_id_fkey FOREIGN KEY (default_layout_id) REFERENCES layout (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE')


def downgrade():
    op.drop_constraint('graph_default_layout_id_fkey', 'graph', type_='foreignkey')
