import json
from datetime import datetime
import networkx as nx
import re


class GSGraph(nx.DiGraph):

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


	def __init__(self, *args, **kwargs):
		super(GSGraph, self).__init__(*args, **kwargs)
		self.json = self.compute_json()

	def compute_json(self):

		self.json = {
			'metadata': self.graph,
			'graph': {
				'nodes': [{ "data": node[1] } for node in self.nodes(data=True)],
				'edges': [{ "data": edge[2] } for edge in self.edges(data=True)],
			}
		}

		return self.json

	def get_json(self):
		return self.json

	def set_json(self, json):
		self.json = json

	def get_name(self):
		return self.graph.get("name", None)

	def set_name(self, name):
		return self.graph.update({"name": name})

	def get_tags(self):
		return self.graph.get("tags", [])

	def set_tags(self, tags):
		return self.graph.update({"tags": tags})

	def add_edge(self, source, target, attr_dict=None):
		attr_dict.update({ "source": source, "target": target })
		super(GSGraph, self).add_edge(source, target, attr_dict)

	def add_node(self, node_name, attr_dict=None):
		attr_dict.update({ "name": node_name, "id": node_name })
		super(GSGraph, self).add_node(node_name, attr_dict)


class GraphSpaceJSONFormat:
	@staticmethod
	def create_gsgraph(json_string):
		"""

		Parameters
		----------
		json_string: json_string to be converted to GSGraph type.

		Returns
		-------
		object: GSGraph

		Notes
		-------
		"""
		graph_json = GraphSpaceJSONFormat.validate_clean_json(json_string)
		G = GSGraph()
		G.graph = graph_json["metadata"]
		for node in graph_json["graph"]["nodes"]:
			G.add_node(node["data"]["name"], attr_dict=node["data"])
		for edge in graph_json["graph"]["edges"]:
			G.add_edge(edge["data"]["source"], edge["data"]["target"], attr_dict=edge["data"])

		G.set_json(graph_json)

		return G

	@staticmethod
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
			if 'label' in node:
				node['content'] = node['label']
				del node['label']
			# If the node has any content inside of it, display that content, otherwise, just make it an empty string
			if 'content' not in node:
				node['content'] = ""

			# we do not use user provided id's anymore. if name is not provided we use ids for name.
			if 'id' in node and 'name' not in node:
				node['name'] = node['id']
				del node['id']

			if "shape" in node:
				shape = node["shape"].lower()
			else:
				shape = "ellipse"

			if shape not in GSGraph.ALLOWED_NODE_SHAPES:
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

			new_edges.append({"data": edge})

		# If name is not provided, name is data
		if 'name' not in old_json['metadata']:
			old_json['metadata']['name'] = "graph_" + str(datetime.now())

		# build the new json
		new_json = {}
		new_json['metadata'] = old_json['metadata']
		new_json['graph'] = {}
		new_json['graph']['nodes'] = new_nodes
		new_json['graph']['edges'] = new_edges

		return json.dumps(new_json, indent=4)

	@staticmethod
	def validate_clean_json(original_json_string):
		"""
		Validates JSON string to see if all required properties for a GraphSpace Graph are provided.
		Cleans the JSON string to the format required for GraphSpace.

		@param original_json_string: JSON string representation of the graph
		"""

		cleaned_json = json.loads(GraphSpaceJSONFormat.clean_graph_json(original_json_string))

		if "graph" not in cleaned_json:
			raise Exception("JSON of graph must have 'graph' property")

		if "nodes" not in cleaned_json["graph"]:
			raise Exception("JSON of graph must have 'nodes' property")

		if not isinstance(cleaned_json["graph"]["nodes"], list):
			raise Exception("Nodes property must contain an array")

		if "edges" not in cleaned_json["graph"]:
			raise Exception("JSON of graph must have 'edges' property")

		if not isinstance(cleaned_json["graph"]["edges"], list):
			raise Exception("Edges property must contain an array")

		# Validate all node properties
		GraphSpaceJSONFormat.validate_node_properties(cleaned_json)

		# Validate all edge properties
		GraphSpaceJSONFormat.validate_edge_properties(cleaned_json)

		return cleaned_json

	@staticmethod
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

	@staticmethod
	def validate_node_properties(original_json):
		"""
		Validates node properties. For example, we no more require all nodes to have a id. But we require all nodes to have a name.
		Old GS graphs will have id property set.

		@param original_json: JSON representation of the graph
		"""

		unique_nodes = set()

		error = ""


		# Go through all nodes to verify if the nodes contain valid properties
		# recognized by CytoscapeJS
		for node in original_json["graph"]["nodes"]:
			node = node["data"]

			# Check to see if name is in node
			if "name" not in node:
				raise Exception("All nodes must have a unique name.  Please verify that all nodes meet this requirement.")

			# Check the data type of node, should be int, float or string
			if not isinstance(node["name"], (basestring, int, float)):
				raise Exception("All nodes must be strings, integers or floats")

			if node["name"] not in unique_nodes:
				unique_nodes.add(node["name"])
			else:
				raise Exception("There are multiple nodes with name: " + str(node["name"]) + ".  Please make sure all node names are unique.")

			# Checks shape of nodes to make sure it contains only legal shapes
			if "shape" in node:
				error += find_property_in_array("Node", node["name"], "shape", node["shape"], GSGraph.ALLOWED_NODE_SHAPES)

			# If node contains a border-style property, check to make sure it is
			# a legal value
			if "border_style" in node:
				error += find_property_in_array("Node", node["name"], "border_style", node["border_style"], GSGraph.ALLOWED_NODE_BORDER_STYLES)

			# If node contains a background_black property, check to make sure
			# they have values [-1, 1]
			if "border_blacken" in node:
				if node["border_blacken"] >= -1 and node["border_blacken"] <= -1:
					error += "Node: " + str(
						node["name"]) + " contains illegal border_blacken value.  Must be between [-1, 1]."

			if "background_repeat" in node:
				error += find_property_in_array("Node", node["name"], "background_repeat", node["background_repeat"],
												GSGraph.ALLOWED_NODE_BACKGROUND_REPEAT)

			if "text_transform" in node:
				error += find_property_in_array("Node", node["name"], "text_transform", node["text_transform"],
												GSGraph.ALLOWED_NODE_TEXT_TRANSFORM)

			if "text_wrap" in node:
				error += find_property_in_array("Node", node["name"], "text_wrap", node["text_wrap"], GSGraph.ALLOWED_NODE_TEXT_WRAP)

			if "text_background_shape" in node:
				error += find_property_in_array("Node", node["name"], "text_background_shape", node["text_background_shape"],
												GSGraph.ALLOWED_NODE_SHAPES)

			if "text_halign" in node:
				error += find_property_in_array("Node", node["name"], "text_halign", node["text_halign"], GSGraph.ALLOWED_TEXT_HALIGN)

			if "text_valign" in node:
				error += find_property_in_array("Node", node["name"], "text_valign", node["text_valign"], GSGraph.ALLOWED_TEXT_VALIGN)

			for attr in GSGraph.NODE_COLOR_ATTRIBUTES:
				if attr in node:
					error += GraphSpaceJSONFormat.check_color_hex(node[attr])

		if len(error) > 0:
			raise Exception(error)
		else:
			return None

	@staticmethod
	def validate_edge_properties(original_json):
		"""
		Validates all edge properties.

		@param original_json: JSON representation of the graph
		"""

		error = ""
		edge_id = None
		node_list = [node["data"]["name"] for node in original_json["graph"]["nodes"]]
		# Go through all edges to verify if edges contain valid properties
		# recognized by CytoscapeJS
		for edge in original_json["graph"]["edges"]:
			edge = edge["data"]

			# Check if source and target node of an edge exist in JSON node list
			if edge["source"] not in node_list or edge["target"] not in node_list:
				raise Exception("For all edges source and target nodes should exist in node list")

			# If edge has no source and target nodes, throw error since they are required
			if "source" not in edge or "target" not in edge:
				raise Exception("All edges must have at least a source and target property.  Please verify that all edges meet this requirement.")

			# Check if source and target nodes are strings, integers or floats
			if not (isinstance(edge["source"], (basestring, int, float)) and isinstance(edge["target"], (basestring, int, float))):
				raise Exception("Source and target nodes of the edge must be strings, integers or floats")

			edge_id = "with source: " + str(edge["source"]) + "and target: " + str(edge["target"])

			# If edge is directed, it must have a target_arrow_shape
			if "directed" in edge and edge["directed"] == "true":
				if "target_arrow_shape" not in edge:
					raise Exception("Edge", edge_id, "must have a target_arrow_shape property if directed is set to true")

			if "source_arrow_shape" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_shape"], GSGraph.ALLOWED_ARROW_SHAPES)

			if "mid_source_arrow_shape" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_shape"], GSGraph.ALLOWED_ARROW_SHAPES)

			if "target_arrow_shape" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["target_arrow_shape"], GSGraph.ALLOWED_ARROW_SHAPES)

			if "mid_target_arrow_shape" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["mid_target_arrow_shape"], GSGraph.ALLOWED_ARROW_SHAPES)

			if "line_style" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["line_style"], GSGraph.ALLOWED_EDGE_STYLES)

			if "source_arrow_fill" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["source_arrow_fill"], GSGraph.ALLOWED_ARROW_FILL)

			if "mid_source_arrow_fill" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["mid_source_arrow_fill"], GSGraph.ALLOWED_ARROW_FILL)

			if "target_arrow_fill" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["target_arrow_fill"], GSGraph.ALLOWED_ARROW_FILL)

			if "mid_target_arrow_fill" in edge:
				error += find_property_in_array("Edge", edge_id, edge, edge["mid_target_arrow_fill"], GSGraph.ALLOWED_ARROW_FILL)

			for attr in GSGraph.EDGE_COLOR_ATTRIBUTES:
				if attr in edge:
					error += GraphSpaceJSONFormat.check_color_hex(edge[attr])

		if len(error) > 0:
			raise Exception(error)
		else:
			return None



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