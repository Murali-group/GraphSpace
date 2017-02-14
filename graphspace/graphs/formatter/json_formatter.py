import json
from datetime import datetime
from graphspace.graphs.classes.gsgraph import GSGraph


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

		error_list = set()

		unique_nodes = set()

		# Go through all nodes to verify if the nodes contain valid properties
		# recognized by CytoscapeJS
		for node in cleaned_json["graph"]["nodes"]:
			try:
				GSGraph.validate_node_properties(node_properties=node["data"], nodes_list=unique_nodes)
				unique_nodes.add(node["data"]["name"])
			except Exception as e:
				error_list.add(str(e))

		# Go through all nodes to verify if the edges contain valid properties
		# recognized by CytoscapeJS
		for edge in cleaned_json["graph"]["edges"]:
			try:
				GSGraph.validate_edge_properties(edge_properties=edge["data"], nodes_list=unique_nodes)
			except Exception as e:
				error_list.add(str(e))

		if len(error_list) > 0:
			raise Exception(", ".join(error_list))
		else:
			return cleaned_json
