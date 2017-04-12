"""add name and label columns to edge table

Revision ID: a2d96d82553f
Revises: afe5e1b13ce5
Create Date: 2017-02-15 16:35:36.971619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2d96d82553f'
down_revision = 'afe5e1b13ce5'
branch_labels = None
depends_on = None


def upgrade():
	# op.add_column('edge', sa.Column('tail_node_name', sa.String))
	# op.add_column('edge', sa.Column('head_node_name', sa.String))
	# op.add_column('edge', sa.Column('tail_node_label', sa.String))
	# op.add_column('edge', sa.Column('head_node_label', sa.String))
	# op.execute('UPDATE edge SET tail_node_name=node.name, tail_node_label=node.label FROM node WHERE edge.tail_node_id=node.id;')
	# op.execute('UPDATE edge SET head_node_name=node.name, head_node_label=node.label FROM node WHERE edge.head_node_id=node.id;')
	# op.alter_column('edge', 'tail_node_name', nullable=False)
	# op.alter_column('edge', 'head_node_name', nullable=False)
	# op.alter_column('edge', 'tail_node_label', nullable=False)
	# op.alter_column('edge', 'head_node_label', nullable=False)
	# Create New Index
	op.create_index('_node_uc_id_name', 'node', ['id','name'], unique=True)
	op.create_index('_node_uc_id_label', 'node', ['id','label'], unique=True)

	op.execute('ALTER TABLE edge ADD CONSTRAINT edge_head_node_id_name_fkey FOREIGN KEY (head_node_id, head_node_name) REFERENCES "node" ( id, name) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE edge ADD CONSTRAINT edge_head_node_id_label_fkey FOREIGN KEY (head_node_id, head_node_label) REFERENCES "node" ( id, label) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE edge ADD CONSTRAINT edge_tail_node_id_name_fkey FOREIGN KEY (tail_node_id, tail_node_name) REFERENCES "node" ( id, name) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')
	op.execute('ALTER TABLE edge ADD CONSTRAINT edge_tail_node_id_label_fkey FOREIGN KEY (tail_node_id, tail_node_label) REFERENCES "node" ( id, label) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE;')


def downgrade():
	op.drop_constraint('edge_head_node_id_name_fkey', 'edge')
	op.drop_constraint('edge_head_node_id_name_fkey', 'edge')
	op.drop_constraint('edge_tail_node_id_name_fkey', 'edge')
	op.drop_constraint('edge_tail_node_id_label_fkey', 'edge')
	op.drop_index('_node_uc_id_name', 'node')
	op.drop_index('_node_uc_id_label', 'node')
