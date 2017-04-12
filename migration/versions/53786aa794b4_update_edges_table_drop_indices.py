"""update edges table - drop indices

Revision ID: 53786aa794b4
Revises: 18108644dac9
Create Date: 2017-02-14 11:46:55.262192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53786aa794b4'
down_revision = '18108644dac9'
branch_labels = None
depends_on = None


def upgrade():
    # Remove index
	op.drop_index('edge_idx_head_label_tail_label', 'edge')
	op.drop_index('edge_idx_head_id_tail_id', 'edge')


def downgrade():
    pass
