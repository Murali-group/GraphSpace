"""convert old json format to new json format

Revision ID: c4c8fd40b021
Revises: 9aecafcc7ca3
Create Date: 2017-02-27 16:03:58.257014

We would like to split our json structures into three types of json structure:

1. Graph Structure
2. Style
3. Node positions

This information will be stored in two tables

1. graph table
	a. graph_json - structure of the graph and their annotations
	b. style_json - base styling of the graph.

2. layout table - layout consists of both location and style information.
	a. positions_json - map of node locations
	b. style_json - styling for the layout


Here is the format of all the three JSON structures:

GRAPH JSON
----------

elements:
	nodes:
		data:
		position:
	edges:
		data:
		position:
data:

POSITIONS JSON
----------

	{
		'<node_id>': {
				'x': 27.22,
				'y': 11.98
			},
			....
	}


STYLE JSON
----------

	[
		{
		  selector: 'node',
		  style: {
			'background-color': 'red'
		  }
		},
		...
	]




The format accepted by GraphSpace will look like this:

elements:
	nodes:
		data:
		positions:
	edges:
		data:
data:
	tags:
	description:
	name:


aand stored in graph JSON on upload:

GRAPH JSON
----------

elements:
	nodes:
		data:
		positions:
	edges:
		data:
data:
	tags:
	description:
	name:


The aim of the migration is to change the following convert from old graph JSON format to new graph JSON format.

OLD graph JSON format looks like this:

graph:
	nodes:
		data:
			id:
			content:
			background_color:
			shape:
			...
		position:
			x:
			y:
	edges:
		data:
			source:
			target:
			background_color:
			shape:
			...
		position:
			x:
			y:
metadata:
	tags:
	description:
	name:

NEW graph JSON format looks like this:

GRAPH JSON
----------

elements:
	nodes:
		data:
			id:
			content:
		position:
			x:
			y:
	edges:
		data:
			source:
			target:
		position:
			x:
			y:
data:
	tags:
	description:
	name:


STYLE JSON
---------

[
	{
		selector: 'node',
		style: {
			'background-color': 'red'
		}
	},
	...
]



OLD layout JSON format looks like two different format:

OLD format 1:
-----------
	{
		'<node_id>': {
				'x': 27.22,
				'y': 11.98
			},
			....
	}

OLD format 2:
-----------
	[
		{
			'x': 27.22,
			'y': 11.98,
			'id': '<node_id>'
		},
			....
	]


NEW layout JSON format looks like this:

positions_json
---------------

{
	'<node_id>': {
			'x': 27.22,
			'y': 11.98
		},
		....
},

style_json
-----------

[
	{
		selector: 'node',
		style: {
			'background-color': 'red'
		}
	},
	...
]


"""
import json
from datetime import datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'c4c8fd40b021'
down_revision = '9aecafcc7ca3'
branch_labels = None
depends_on = None

graphhelper1 = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
)

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('json', sa.String),
	sa.Column('graph_json', sa.String),
	sa.Column('style_json', sa.String)
)

layouthelper = sa.Table(
	'layout',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('graph_id', sa.Integer),
	sa.Column('name', sa.String),
	sa.Column('owner_email', sa.String),
	sa.Column('is_shared', sa.String),
	sa.Column('json', sa.String),
	sa.Column('style_json', sa.String)
)

node_data_attr_to_style_attr_map = {
	'width': 'width',
	'height': 'height',
	'shape': 'shape',
	'background_color': 'background-color',
	'background_blacken': 'background-blacken',
	'background_opacity': 'background-opacity',
	'border_width': 'border-width',
	'border_style': 'border-style',
	'border_color': 'border-color',
	'border_opacity': 'border-opacity',

	'background_image': 'background-image',
	'background_image_opacity': 'background-image-opacity',
	'background_width': 'background-width',
	'background_height': 'background-height',
	'background_fit': 'background-fit',
	'background_repeat': 'background-repeat',
	'background_position_x': 'background-position-x',
	'background_position_y': 'background-position-y',
	'background_clip': 'background-clip',

	'color': 'color',
	# 'content': 'content',
	'font_family': 'font-family',
	'font_size': 'font-size',
	'font_style': 'font-style',
	'font_weight': 'font-weight',
	'text_transform': 'text-transform',
	'text_wrap': 'text-wrap',
	'text_max_width': 'text-max-width',
	'edge_text_rotation': 'edge-text-rotation',

	'text_opacity': 'text-opacity',
	'text_outline_color': 'text-outline-color',
	'text_outline_opacity': 'text-outline-opacity',
	'text_outline_width': 'text-outline-width',
	'text_shadow_blur': 'text-shadow-blur',
	'text_shadow_color': 'text-shadow-color',
	'text_shadow_offset_x': 'text-shadow-offset-x',
	'text_shadow_offset_y': 'text-shadow-offset-y',
	'text_shadow_opacity': 'text-shadow-opacity',
	'text_background_shape': 'text-background-shape',
	'text_border_width': 'text-border-width',
	'text_border_style': 'text-border-style',
	'text_border_color': 'text-border-color',
	'min_zoomed_font_size': 'min-zoomed-font-size',
	'text_halign': 'text-halign',
	'text_valign': 'text-valign'
}

edge_data_attr_to_style_attr_map = {
	'color': 'line-color',

	'width': 'width',
	'curve_style': 'curve-style',
	'haystack_radius': 'haystack-radius',
	'control_point_step_size': 'control-point-step-size',
	'control_point_distance': 'control-point-distance',
	'control_point_weight': 'control-point-weight',
	'line_color': 'line-color',
	'line_style': 'line-style',

	'source_arrow_color': 'source-arrow-color',
	'source_arrow_shape': 'source-arrow-shape',
	'source_arrow_fill': 'source-arrow-fill',
	'mid_source_arrow_color': 'mid-source-arrow-color',
	'mid_source_arrow_shape': 'mid-source-arrow-shape',
	'mid_source_arrow_fill': 'mid-source-arrow-fill',
	'target_arrow_color': 'target-arrow-color',
	'target_arrow_shape': 'target-arrow-shape',
	'target_arrow_fill': 'target-arrow-fill',
	'mid_target_arrow_color': 'mid-target-arrow-color',
	'mid_target_arrow_fill': 'mid-target-arrow-fill',
}


def clean_graph_json(original_json_string):
	"""
		Converts original_json_string such that its compatible with Cytoscape.js and Graphspace's json format.

		See: http://cytoscape.github.io/cytoscape.js/

		Original json structure used for Cytoscape Web:
		{
			"metadata": {

			},

			"graph": {
				"data": {
					"nodes": [
						{ "id": "node1", "label": "n1", ... },
						{ "id": "node2", "label": "n2", ... },
						...
					],
					"edges": [
						{ "id": "edge1", "label": "e1", ... },
						{ "id": "edge2", "label": "e2", ... },
						...
					]
				}
			}
		}

		New json structure:
		{
			"metadata": {

			},

			"graph": {
				"nodes": [
					{"data": {"name": "node1", "content": "n1", ...}},
					{"data": {"name": "node2", "content": "n2", ...}},
					...
				],
				"edges": [
					{"data": {"name": "edge1", "content": "e1", ...}},
					{"data": {"name": "edge2", "content": "e2", ...}},
					...
				]
			}
		}
	"""

	# parse old json data
	old_json = json.loads(original_json_string)

	if 'data' in old_json['graph'] and 'nodes' in old_json['graph']['data']:
		old_nodes = old_json['graph']['data']['nodes']
		old_edges = old_json['graph']['data']['edges']
	elif 'nodes' in old_json['graph'] and 'edges' in old_json['graph']:
		old_nodes = [node['data'] for node in old_json['graph']['nodes']]
		old_edges = [edge['data'] for edge in old_json['graph']['edges']]
	else:
		raise Exception("JSON of graph must have 'nodes' and 'edges' property")

	new_nodes, new_edges = [], []

	# format node and edge data
	for node in old_nodes:
		# Used for backwards-compatibility since some JSON have label
		# but new CytoscapeJS uses the content property
		if 'content' in node:
			node['label'] = node['content']
			del node['content']
		# If the node has any content inside of it, display that content, otherwise, just make it an empty string
		if 'label' not in node:
			node['label'] = ""

		# we do not use user provided id's anymore. if name is not provided we use ids for name.
		if 'id' in node and 'name' not in node:
			node['name'] = node['id']

		if "shape" in node:
			shape = node["shape"].lower()
		else:
			shape = "ellipse"

		if shape not in ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
		                 'pentagon', 'hexagon', 'heptagon', 'octagon', 'star',
		                 'diamond', 'vee', 'rhomboid']:
			shape = "ellipse"

		node["shape"] = shape

		new_nodes.append({"data": node})

	edge_names = []
	for edge in old_edges:
		# Assignes names to the edges to be the names of the nodes that they are attached to.
		# To make sure int and floats are also accepted as source and target nodes of an edge
		source_node = str(edge['source']) if "source" in edge else ""
		target_node = str(edge['target']) if "target" in edge else ""
		edge['name'] = source_node + '-' + target_node

		# If the ID has not yet been seen (is unique), simply store the ID
		# of that edge as source-target
		if edge['name'] not in edge_names:
			edge_names.append(edge['name'])
		else:
			# Otherwise if there are multiple edges with the same ID,
			# append a number to the end of the ID so we can distinguish
			# multiple edges having the same source and target.
			# This needs to be done because HTML DOM needs unique IDs.
			counter = 0
			while edge['name'] in edge_names:
				counter += 1
				edge['name'] = edge['name'] + str(counter)
			edge_names.append(edge['name'])

		if 'target_arrow_shape' not in edge:
			edge['target_arrow_shape'] = "none"

		if "is_directed" not in edge:
			if edge['target_arrow_shape'] == "none":
				edge['is_directed'] = 0
			else:
				edge['is_directed'] = 1

		new_edges.append({"data": edge})

	# If name is not provided, name is data
	if 'name' not in old_json['metadata']:
		old_json['metadata']['name'] = "graph_" + str(datetime.now())

	# build the new json
	new_json = {}
	new_json['data'] = old_json['metadata']
	new_json['elements'] = {}
	new_json['elements']['nodes'] = new_nodes
	new_json['elements']['edges'] = new_edges

	return new_json


def parse_old_graph_json(old_graph_json):
	old_graph_json = clean_graph_json(old_graph_json)

	new_graph_json = {
		'data': old_graph_json['data'],
		'elements': {
			'nodes': [],
			'edges': []
		}
	}

	style_json = []
	for node in old_graph_json['elements']['nodes']:
		node_style = {
			'selector': "node[name = '%s']" % node['data']['name'],
			'style': {}
		}
		for attr in node_data_attr_to_style_attr_map.keys():
			attr_val = node['data'].pop(attr, None)
			if attr_val is not None:
				node_style['style'][node_data_attr_to_style_attr_map[attr]] = attr_val

		if len(node_style['style'].keys()) > 0:
			style_json.append(node_style)

		new_graph_json['elements']['nodes'].append(node)

	for edge in old_graph_json['elements']['edges']:
		if 'name' not in edge['data']:
			edge['data']['name'] = '%s-%s' % (edge['data']['source'], edge['data']['target'])

		edge_style = {
			'selector': "edge[name = '%s']" % edge['data']['name'],
			'style': {}
		}
		for attr in edge_data_attr_to_style_attr_map.keys():
			attr_val = edge['data'].pop(attr, None)
			if attr_val is not None:
				edge_style['style'][edge_data_attr_to_style_attr_map[attr]] = attr_val

		if len(edge_style['style'].keys()) > 0:
			style_json.append(edge_style)

		new_graph_json['elements']['edges'].append(edge)

	return new_graph_json, style_json


def construct_new_layout_json(old_layout_json):
	new_layout_json = {}

	if isinstance(old_layout_json, dict):
		new_layout_json = old_layout_json
	else:
		for obj in old_layout_json:
			new_layout_json[obj['id']] = {
				'x': obj['x'],
				'y': obj['y'],
			}

	return new_layout_json


def upgrade():
	# we build a quick link for the current connection of alembic
	connection = op.get_bind()
	print('started')
	op.add_column('layout', sa.Column('style_json', sa.String))
	op.add_column('graph', sa.Column('graph_json', sa.String))
	op.add_column('graph', sa.Column('style_json', sa.String))

	graphtotal = connection.execute(graphhelper1.select()).rowcount
	offset = 0
	while offset < graphtotal:
		for graph in connection.execute(graphhelper.select().order_by("id").limit(100).offset(offset)):
			graph_json, style_json = parse_old_graph_json(graph.json)
			connection.execute(graphhelper.update().where(graphhelper.c.id == graph.id).values(
				graph_json=json.dumps(graph_json),
				style_json=json.dumps({
					"format_version": "1.0",
					"generated_by": "graphspace-2.0.0",
					"target_cytoscapejs_version": "~2.1",
					'style': style_json
				})))
		offset += 100

	for layout in connection.execute(layouthelper.select()):
		for graph in connection.execute(graphhelper.select().where(graphhelper.c.id == layout.graph_id)):
			new_json = construct_new_layout_json(json.loads(layout.json))
			connection.execute(
				layouthelper.update().where(
					layouthelper.c.id == layout.id
				).values(
					json=json.dumps(new_json),
					style_json=graph.style_json
				)
			)

	op.alter_column('graph', 'graph_json', nullable=False)
	op.alter_column('layout', 'style_json', nullable=False)

	op.alter_column('layout', 'json', new_column_name='positions_json')

	op.alter_column('graph', 'json', nullable=True)


def downgrade():
	# connection = op.get_bind()

	# connection.execute(
	# 		layouthelper.delete().where(
	# 			layouthelper.c.name == 'initial_layout'
	# 		)
	# )

	op.execute('delete from graph where json is NULL;')
	op.drop_column('layout', 'style_json')
	op.drop_column('graph', 'style_json')
	op.drop_column('graph', 'graph_json')

	op.alter_column('graph', 'json', nullable=False)

	op.alter_column('layout', 'positions_json', new_column_name='json')
