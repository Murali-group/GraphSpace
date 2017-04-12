import json
import re

# See http://js.cytoscape.org/#style/node-body
ALLOWED_NODE_SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
                       'pentagon', 'hexagon', 'heptagon', 'octagon', 'star',
                       'diamond', 'vee', 'rhomboid']

ALLOWED_NODE_BORDER_STYLES = ['solid', 'dotted', 'dashed', 'double']

ALLOWED_NODE_BACKGROUND_REPEAT = ['no-repeat', 'repeat-x', 'repeat-y', 'repeat']

ALLOWED_NODE_TEXT_TRANSFORM = ['none', 'uppercase', 'lowercase']

ALLOWED_NODE_TEXT_WRAP = ['none', 'wrap']

ALLOWED_TEXT_BACKROUND_SHAPE = ['rectangle', 'roundrectangle']

ALLOWED_TEXT_HALIGN = ['left', 'center', 'right']

ALLOWED_TEXT_VALIGN = ['top', 'center', 'bottom']

## See http://js.cytoscape.org/#style/labels
ALLOWED_TEXT_WRAP = ['wrap', 'none']

## See http://js.cytoscape.org/#style/edge-arrow
ALLOWED_ARROW_SHAPES = ['tee', 'triangle', 'triangle-tee', 'triangle-backcurve',
                        'square', 'circle', 'diamond', 'none']

## See http://js.cytoscape.org/#style/edge-line
ALLOWED_EDGE_STYLES = ['solid', 'dotted', 'dashed']

ALLOWED_ARROW_FILL = ['filled', 'hollow']

NODE_COLOR_ATTRIBUTES = ['background_color', 'border_color', 'color',
                         'text_outline_color', 'text_shadow_color',
                         'text_border_color']

EDGE_COLOR_ATTRIBUTES = ['line_color', 'source_arrow_color',
                         'mid_source_arrow_color', 'target_arrow_color',
                         'mid_target_arrow_color']


def verify_json(graph_json):
	graph_json = json.loads(graph_json)

	for node in graph_json["graph"]["nodes"]:
		node = node["data"]

		if "shape" in node:
			shape = node["shape"].lower()
		else:
			shape = "ellipse"

		if shape not in ALLOWED_NODE_SHAPES:
			shape = "ellipse"

		node["shape"] = shape

	return json.dumps(graph_json)


def validate_clean_json(json_string):
	"""
	Validates JSON to see if all properties are consistent with API.

	@param graphJson: JSON of graph
	"""

	cleaned_json = json.loads(clean_graph_json(json_string))

	if "graph" not in cleaned_json:
		return "JSON of graph must have 'graph' property"

	if "nodes" not in cleaned_json["graph"]:
		return "JSON of graph must have 'nodes' property"

	if not isinstance(cleaned_json["graph"]["nodes"], list):
		return "Nodes property must contain an array"

	if "edges" not in cleaned_json["graph"]:
		return "JSON of graph must have 'edges' property"

	if not isinstance(cleaned_json["graph"]["edges"], list):
		return "Edges property must contain an array"

	# Validate all node properties
	nodes = cleaned_json["graph"]["nodes"]
	error = validate_node_properties(nodes)

	if error is not None:
		return None, error

	# Validate all edge properties
	error = validate_edge_properties(cleaned_json["graph"]["edges"], nodes)

	if error is not None:
		return None, error

	# Attach ID's to each edge for traversing the element
	cleaned_json = assign_edge_ids(cleaned_json)

	return cleaned_json, None


def validate_edge_properties(edges, nodes):
	"""
	Validates all edge properties.

	@param edges: Array of edge objects (http://js.cytoscape.org)
	"""

	error = ""
	edge_id = None
	node_list = [node["data"]["id"] for node in nodes]
	# Go through all edges to verify if edges contain valid properties
	# recognized by CytoscapeJS
	for edge in edges:
		edge = edge["data"]

		# Check if source and target node of an edge exist in JSON node list
		if edge["source"] not in node_list or edge["target"] not in node_list:
			return "For all edges source and target nodes should exist in node list"

		# If edge has no source and target nodes, throw error since they are required
		if "source" not in edge or "target" not in edge:
			return "All edges must have at least a source and target property.  Please verify that all edges meet this requirement."

		# Check if source and target nodes are strings, integers or floats
		if not (isinstance(edge["source"], (basestring, int, float)) and isinstance(edge["target"],
		                                                                            (basestring, int, float))):
			return "Source and target nodes of the edge must be strings, integers or floats"

		edge_id = "with source: " + str(edge["source"]) + "and target: " + str(edge["target"])

		# If edge is directed, it must have a target_arrow_shape
		if "directed" in edge and edge["directed"] == "true":
			if "target_arrow_shape" not in edge:
				return "Edge", edge_id, "must have a target_arrow_shape property if directed is set to true"

		if "source_arrow_shape" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_shape"], ALLOWED_ARROW_SHAPES)

		if "mid_source_arrow_shape" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_shape"], ALLOWED_ARROW_SHAPES)

		if "target_arrow_shape" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["target_arrow_shape"], ALLOWED_ARROW_SHAPES)

		if "mid_target_arrow_shape" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["mid_target_arrow_shape"], ALLOWED_ARROW_SHAPES)

		if "line_style" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["line_style"], ALLOWED_EDGE_STYLES)

		if "source_arrow_fill" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_fill"], ALLOWED_ARROW_FILL)

		if "mid_source_arrow_fill" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["mid_source_arrow_fill"], ALLOWED_ARROW_FILL)

		if "target_arrow_fill" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["target_arrow_fill"], ALLOWED_ARROW_FILL)

		if "mid_target_arrow_fill" in edge:
			error += find_property_in_array("Edge", edge_id, edge, edge["mid_target_arrow_fill"], ALLOWED_ARROW_FILL)

		for attr in EDGE_COLOR_ATTRIBUTES:
			if attr in edge:
				error += check_color_hex(edge[attr])

	if len(error) > 0:
		return error
	else:
		return None


def validate_node_properties(nodes):
	"""
	Validates all node properties.

	:param G: NetworkX object.
	"""

	unique_ids = set()

	error = ""

	# Go through all nodes to verify if the nodes contain valid properties
	# recognized by CytoscapeJS
	for node in nodes:
		node = node["data"]
		# Check the data type of node, should be int, float or string
		if not isinstance(node["id"], (basestring, int, float)):
			return "All nodes must be strings, integers or floats"

		# Check to see if ID is in node
		if "id" not in node:
			return "All nodes must have a unique ID.  Please verify that all nodes meet this requirement."

		if node["id"] not in unique_ids:
			unique_ids.add(node["id"])
		else:
			return "There are multiple nodes with ID: " + str(
				node["id"]) + ".  Please make sure all node IDs are unique."

		# Checks shape of nodes to make sure it contains only legal shapes
		if "shape" in node:
			error += find_property_in_array("Node", node["id"], "shape", node["shape"], ALLOWED_NODE_SHAPES)

		# If node contains a border-style property, check to make sure it is
		# a legal value
		if "border_style" in node:
			error += find_property_in_array("Node", node["id"], "border_style", node["border_style"],
			                                ALLOWED_NODE_BORDER_STYLES)

		# If node contains a background_black property, check to make sure
		# they have values [-1, 1]
		if "border_blacken" in node:
			if node["border_blacken"] >= -1 and node["border_blacken"] <= -1:
				error += "Node: " + str(
					node["id"]) + " contains illegal border_blacken value.  Must be between [-1, 1]."

		if "background_repeat" in node:
			error += find_property_in_array("Node", node["id"], "background_repeat", node["background_repeat"],
			                                ALLOWED_NODE_BACKGROUND_REPEAT)

		if "text_transform" in node:
			error += find_property_in_array("Node", node["id"], "text_transform", node["text_transform"],
			                                ALLOWED_NODE_TEXT_TRANSFORM)

		if "text_wrap" in node:
			error += find_property_in_array("Node", node["id"], "text_wrap", node["text_wrap"], ALLOWED_NODE_TEXT_WRAP)

		if "text_background_shape" in node:
			error += find_property_in_array("Node", node["id"], "text_background_shape", node["text_background_shape"],
			                                ALLOWED_NODE_SHAPES)

		if "text_halign" in node:
			error += find_property_in_array("Node", node["id"], "text_halign", node["text_halign"], ALLOWED_TEXT_HALIGN)

		if "text_valign" in node:
			error += find_property_in_array("Node", node["id"], "text_valign", node["text_valign"], ALLOWED_TEXT_VALIGN)

		for attr in NODE_COLOR_ATTRIBUTES:
			if attr in node:
				error += check_color_hex(node[attr])

	if len(error) > 0:
		return error
	else:
		return None


def check_color_hex(color_code):
	"""
	Check the validity of the hexadecimal code of various node and edge color
	related attributes.

	This function returns an error if the hexadecimal code is not of the format
	'#XXX' or '#XXXXXX', i.e. hexadecimal color code is not valid.

	:param color_code: color code
	"""
	# if color name is given instead of hex code, no need to check its validity
	if not color_code.startswith('#'):
		return ""
	valid = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_code)
	if valid is None:
		return color_code + ' is not a valid hex color code.'
	else:
		return ""


def find_property_in_array(elementType, key, prop, value, array):
	"""
	Goes through array to see if property is contained in the array.

	:param elementType: Node or an Edge
	:param key: Key to search for in network
	:param value: Value of key
	:param prop: Name to search for in array
	:param array: Array to search for property in
	"""
	if value not in array:
		array_list = ",".join(array)
		return elementType + " " + key + " contains illegal value for property: " + prop + ".  Value given for this property was: " + value + ".  Accepted values for property: " + prop + " are: [" + array_list + "]"
	else:
		return ""


def assign_edge_names(graph_json):
	'''
		Assignes names to the edges to be the names of the nodes that they are attached to.

		:param graph_json: JSON of graph
		:return graph_json: JSON of graph having unique ID's for all edges
	'''

	ids = []
	# Creates ID's for all of the edges by creating utilizing the source and target nodes
	# The edge ID would have the form: source-target
	for edge in graph_json['graph']['edges']:
		# To make sure int and floats are also accepted as source and target nodes of an edge
		source_node = str(edge['data']['source'])
		target_node = str(edge['data']['target'])
		edge['data']['name'] = source_node + '-' + target_node

		# If the ID has not yet been seen (is unique), simply store the ID
		# of that edge as source-target
		if edge['data']['name'] not in ids:
			ids.append(edge['data']['name'])
		else:
			# Otherwise if there are multiple edges with the same ID,
			# append a number to the end of the ID so we can distinguish
			# multiple edges having the same source and target.
			# This needs to be done because HTML DOM needs unique IDs.
			counter = 0
			while edge['data']['name'] in ids:
				counter += 1
				edge['data']['name'] = edge['data']['name'] + str(counter)
			ids.append(edge['data']['name'])

	# Return JSON having all edges containing unique ID's
	return graph_json


# This file is a wrapper to communicate with sqlite3 database
# that does not need authentication for connection.

# It may be viewed as the controller to the database

def convert_json(original_json):
	'''
		Converts original_json that's used in Cytoscape Web
		such that it is compatible with the new Cytoscape.js

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
					{"data": {"id": "node1", "content": "n1", ...}},
					{"data": {"id": "node2", "content": "n2", ...}},
					...
				],
				"edges": [
					{"data": {"id": "edge1", "content": "e1", ...}},
					{"data": {"id": "edge2", "content": "e2", ...}},
					...
				]
			}
		}
	'''


	# parse old json data
	old_json = json.loads(original_json)
	old_nodes = old_json['graph']['data']['nodes']
	old_edges = old_json['graph']['data']['edges']

	new_nodes, new_edges = [], []

	# format node and edge data
	for node in old_nodes:
		# Used for backwards-compatibility since some JSON have label
		# but new CytoscapeJS uses the content property
		if 'label' in node:
			node['content'] = node['label']
			del node['label']
		# If the node has any content inside of it, display that content, otherwise, just make it an empty string
		if 'content' not in node['data']:
			node['data']['content'] = ""

		new_nodes.append({"data": node})

	for edge in old_edges:
		new_edges.append({"data": edge})

	# build the new json
	new_json = {}
	new_json['metadata'] = old_json['metadata']
	new_json['graph'] = {}
	new_json['graph']['nodes'] = new_nodes
	new_json['graph']['edges'] = new_edges

	return json.dumps(new_json, indent=4)


def clean_graph_json(original_json_string):
	'''
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
					{"data": {"id": "node1", "content": "n1", ...}},
					{"data": {"id": "node2", "content": "n2", ...}},
					...
				],
				"edges": [
					{"data": {"id": "edge1", "content": "e1", ...}},
					{"data": {"id": "edge2", "content": "e2", ...}},
					...
				]
			}
		}
	'''

	# parse old json data
	old_json = json.loads(original_json_string)

	if 'data' in old_json['graph']:
		old_nodes = old_json['graph']['data']['nodes']
		old_edges = old_json['graph']['data']['edges']
	else:
		old_nodes = [node['data'] for node in old_json['graph']['nodes']]
		old_edges = [edge['data'] for edge in old_json['graph']['edges']]

	new_nodes, new_edges = [], []

	# format node and edge data
	for node in old_nodes:
		# Used for backwards-compatibility since some JSON have label
		# but new CytoscapeJS uses the content property
		if 'label' in node:
			node['content'] = node['label']
			del node['label']
		# If the node has any content inside of it, display that content, otherwise, just make it an empty string
		if 'content' not in node:
			node['content'] = ""

		new_nodes.append({"data": node})

	for edge in old_edges:
		new_edges.append({"data": edge})

	# build the new json
	new_json = {}
	new_json['metadata'] = old_json['metadata']
	new_json['graph'] = {}
	new_json['graph']['nodes'] = new_nodes
	new_json['graph']['edges'] = new_edges

	return json.dumps(new_json, indent=4)
