"""add nodes and egdes for graphs with missing nodes/edges in database

Some of the graphs dont have respective nodes and edges in the edges table. This script will create node and edges in the respective node/edges table.

Revision ID: 7df7ee83a212
Revises: c4c8fd40b021
Create Date: 2017-03-10 10:54:51.546356

"""
import json

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from graphspace_python.graphs.formatter.json_formatter import CyJSFormat

revision = '7df7ee83a212'
down_revision = 'c4c8fd40b021'
branch_labels = None
depends_on = None

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('graph_json', sa.String)
)

nodehelper = sa.Table(
	'node',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('label', sa.String),
	sa.Column('name', sa.String),
	sa.Column('graph_id', sa.Integer),
)

edgehelper = sa.Table(
	'edge',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('name', sa.String),
	sa.Column('head_node_id', sa.Integer),
	sa.Column('tail_node_id', sa.Integer),
	sa.Column('tail_node_name', sa.String),
	sa.Column('head_node_name', sa.String),
	sa.Column('tail_node_label', sa.String),
	sa.Column('head_node_label', sa.String),
	sa.Column('graph_id', sa.Integer),
	sa.Column('is_directed', sa.Integer),
)


def add_node(connection, name, label, graph_id):
	res = connection.execute(nodehelper.insert().values(name=name, label=label, graph_id=graph_id))
	node_id = res.inserted_primary_key
	for node in connection.execute(nodehelper.select().where(nodehelper.c.id==node_id[0])):
		return node.id, node.name, node.label


def add_graph_nodes(connection, graph_id, nodes):
	node_name_to_id_map = dict()
	node_id_to_label_map = dict()

	for node in nodes:
		# Add node to table
		id, name, label = add_node(connection, name=node[0], label=node[1]['data']['label'], graph_id=graph_id)
		node_name_to_id_map[name] = id
		node_id_to_label_map[id] = label
	return node_name_to_id_map, node_id_to_label_map


def add_edge(connection, name, head_node_id, tail_node_id, tail_node_name, head_node_name, tail_node_label,
             head_node_label, is_directed, graph_id):
	connection.execute(edgehelper.insert().values(
		name=name,
		head_node_id=head_node_id,
		tail_node_id=tail_node_id,
		tail_node_name=tail_node_name,
		head_node_name=head_node_name,
		tail_node_label=tail_node_label,
		head_node_label=head_node_label,
		is_directed=is_directed,
		graph_id=graph_id))


def add_graph_edges(connection, graph_id, edges, node_name_to_id_map, node_id_to_label_map):
	edge_name_to_id_map = dict()
	for edge in edges:
		is_directed = 0 if 'is_directed' not in edge[2]['data'] else 1 if edge[2]['data']['is_directed'] else 0

		# To make sure int and floats are also accepted as source and target nodes of an edge
		add_edge(connection,
		         graph_id=graph_id,
		         head_node_id=str(node_name_to_id_map[edge[1]]),
		         tail_node_id=str(node_name_to_id_map[edge[0]]),
		         head_node_name=str(edge[1]),
		         tail_node_name=str(edge[0]),
		         head_node_label=str(node_id_to_label_map[node_name_to_id_map[edge[1]]]),
		         tail_node_label=str(node_id_to_label_map[node_name_to_id_map[edge[0]]]),
		         name=str(edge[2]['data']['name']),
		         is_directed=is_directed)


def upgrade():
	connection = op.get_bind()
	graph_ids = set()

	for graph in connection.execute(graphhelper.select().distinct(graphhelper.c.id)):
		graph_ids.add(graph.id)

	graphs_with_elements = set()

	for node in connection.execute(nodehelper.select().distinct(nodehelper.c.graph_id)):
		graphs_with_elements.add(node.graph_id)

	graph_ids.difference_update(graphs_with_elements)

	for edge in connection.execute(edgehelper.select().distinct(edgehelper.c.graph_id)):
		graphs_with_elements.add(edge.graph_id)

	graph_ids.difference_update(graphs_with_elements)

	for graph in connection.execute(graphhelper.select().where(graphhelper.c.id.in_(graph_ids))):
		print(graph.id)
		G = CyJSFormat.create_gsgraph(graph.graph_json)
		# Add graph nodes
		node_name_to_id_map, node_id_to_label_map = add_graph_nodes(connection, graph.id, G.nodes(data=True))
		# Add graph edges
		edge_name_to_id_map = add_graph_edges(connection, graph.id, G.edges(data=True), node_name_to_id_map,
		                                      node_id_to_label_map)


def downgrade():
	pass
