"""Update style json

Revision ID: bb9a45e2ee5e
Revises: 755438125e7d
Create Date: 2017-04-20 21:46:41.278082

"""
import json

from datetime import datetime

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'bb9a45e2ee5e'
down_revision = '755438125e7d'
branch_labels = None
depends_on = None


graphhelper1 = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('is_public', sa.Integer),
)

graphhelper = sa.Table(
	'graph',
	sa.MetaData(),
	sa.Column('id', sa.Integer, primary_key=True),
	sa.Column('json', sa.String),
	sa.Column('style_json', sa.String),
	sa.Column('is_public', sa.Integer),
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


def upgrade():
    # we build a quick link for the current connection of alembic
	connection = op.get_bind()

	graphtotal = connection.execute(graphhelper1.select().where(graphhelper1.c.is_public == 1)).rowcount
	offset = 0
	while offset < graphtotal:
		for graph in connection.execute(graphhelper.select().where(graphhelper.c.is_public == 1).order_by("id").limit(100).offset(offset)):
			graph_json, style_json = parse_old_graph_json(graph.json)
			connection.execute(graphhelper.update().where(graphhelper.c.id == graph.id).values(
				style_json=json.dumps({
					"format_version": "1.0",
					"generated_by": "graphspace-2.0.0",
					"target_cytoscapejs_version": "~2.1",
					'style': style_json
				})))
		offset += 100


def downgrade():
    pass
