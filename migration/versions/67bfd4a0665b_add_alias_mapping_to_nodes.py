"""add alias mapping to nodes
and updating graph name.

Revision ID: 67bfd4a0665b
Revises: 97a32c589371
Create Date: 2017-04-09 04:29:24.868096

"""
import json

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '67bfd4a0665b'
down_revision = '7df7ee83a212'
# down_revision = '97a32c589371'
branch_labels = None
depends_on = None

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('name', sa.String),
	sa.Column('graph_json', sa.String)
)
graphhelper1 = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
)

uniprothelper = sa.Table(
	'uniprot_alias',
	sa.MetaData(),
	sa.Column('accession_number', sa.String, primary_key=True),
	sa.Column('alias_name', sa.String),
	sa.Column('alias_source', sa.String)
)


def upgrade():
	connection = op.get_bind()

	graphtotal = connection.execute(graphhelper1.select()).rowcount
	offset = 0
	while offset < graphtotal:
		for graph in connection.execute(graphhelper.select().order_by("id").limit(100).offset(offset)):
			graph_json = json.loads(graph.graph_json)
			if 'elements' in graph_json and 'nodes' in graph_json['elements']:
				for node in graph_json['elements']['nodes']:
					if 'data' in node and 'aliases' not in 'data':
						node['data']['aliases'] = []
						for uniprot_mapping in connection.execute(
								uniprothelper.select().where(uniprothelper.c.accession_number == str(node['data']['id']))):
							node['data']['aliases'].append(uniprot_mapping.alias_source + ':' + uniprot_mapping.alias_name)

			if 'data' in graph_json and 'title' in graph_json['data'] and len(graph_json['data']['title'].strip()) > 0:
				graph_json['data']['title'] = graph_json['data']['title']
			elif 'data' in graph_json and 'name' in graph_json['data'] and len(graph_json['data']['name'].strip()) > 0:
				graph_json['data']['title'] = graph_json['data']['name']
			else:
				graph_json['data']['title'] = ''

			graph_json['data']['name'] = graph.name

			connection.execute(
				graphhelper.update().where(
					graphhelper.c.id == graph.id
				).values(
					graph_json=json.dumps(graph_json)
				)
			)
		offset += 100



def downgrade():
	pass
