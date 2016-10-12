from datetime import datetime

import applications.graphs.dal as db
import applications.users as users
from graphspace.wrappers import atomic_transaction
from json_validator import *

AUTOMATIC_LAYOUT_ALGORITHMS = [ 'default_breadthfirst', 'default_concentric', 'default_circle', 'default_cose', 'default_grid' ]


def get_graph(request, graph_owner, graphname):
	graph = db.get_graph(request.db_session, graph_owner, graphname) if graphname is not None and graph_owner is not None else None
	# TODO: Check if we need verify json function call or not.
	if graph is not None:
		graph.json = verify_json(graph.json)
	return graph


def get_graph_by_id(request, graph_id):
	return db.get_graph_by_id(request.db_session, graph_id)


def is_user_authorized_to_view_graph(request, username, graph_id):
	is_authorized = False

	graph = db.get_graph_by_id(request.db_session, graph_id)

	if graph is not None:  # Graph doesnt exists
		if graph.owner_email == username:
			is_authorized = True
		elif graph.is_public == 1:  # graph is public
			is_authorized = True
		else:  # graph is not public
			for group in graph.groups:
				if users.controllers.is_member_of_group(request, username, group.id):
					is_authorized = True
	return is_authorized


def search_graphs_shared_with_user(request, uid, search_type, search_terms, tags, order_by, page, page_size):
	user = users.controllers.get_user(request, uid)

	if user is None:
		return []
	else:
		edges, nodes, names = [], [], []
		for term in search_terms:
			if ':' in term:
				edges.append(term)
			else:
				names.append(term)
				nodes.append(term)

		return db.get_graphs_by_edges_and_nodes_and_names(request.db_session, group_ids=[group.id for group in user.member_groups], names=filter(None, names), nodes=filter(None, nodes), edges=edges, page=page, page_size=page_size, partial_matching=True if search_type == 'partial_search' else False, order=_convert_order_query_term_to_database_order_object(order_by), tags=tags)


def search_graphs_owned_by_user(request, uid, search_type, search_terms, tags, order_by, page, page_size):
	if uid is None:
		return []
	else:
		edges, nodes, names = [], [], []
		for term in search_terms:
			if ':' in term:
				edges.append(term)
			else:
				names.append(term)
				nodes.append(term)

		return db.get_graphs_by_edges_and_nodes_and_names(request.db_session, owner_email=uid, names=filter(None, names), nodes=filter(None, nodes), edges=edges, page=page, page_size=page_size, partial_matching=True if search_type == 'partial_search' else False, order=_convert_order_query_term_to_database_order_object(order_by), tags=tags)


def search_public_graphs(request, uid, search_type, search_terms, tags, order_by, page, page_size):

	edges, nodes, names = [], [], []
	for term in search_terms:
		if ':' in term:
			edges.append(term)
		else:
			names.append(term)
			nodes.append(term)

	return db.get_graphs_by_edges_and_nodes_and_names(request.db_session, is_public=1, names=filter(None, names), nodes=filter(None, nodes), edges=edges, page=page, page_size=page_size, partial_matching=True if search_type == 'partial_search' else False, order=_convert_order_query_term_to_database_order_object(order_by), tags=tags)


def uploadJSONFile(request, username, graphJSON, title):
	"""
		Uploads JSON file to GraphSpace via /upload.

		@param username: Owner of graph
		@param graphJSON: JSON of graph
		@param title: Title of graph

	"""

	# Loads JSON format
	parseJson = json.loads(graphJSON)

	# Creates metadata tag
	if 'metadata' not in parseJson:
		parseJson['metadata'] = {}

	# If name is not provided, name is data
	if 'name' not in parseJson['metadata']:
		parseJson['metadata']['name'] = "graph_" + str(datetime.now())

	title = title or parseJson['metadata']['name']

	is_public = 1 if username is None else 0
	username = users.controllers.add_user(request).email if username is None else username

	return add_graph(request, username, title, json.dumps(parseJson), public=is_public)

@atomic_transaction
def add_graph(request, username, graphname, graph_json_string, created=None, modified=None, public=0, shared_with_groups=0, default_layout_id=None):
	"""
		Inserts a uniquely named graph under a username.

		:param username: Email of user in GraphSpace
		:param graphname: Name of graph to insert
		:param graph_json: JSON of graph
		:param created: When was graph created
		:param public: Is graph public?
		:param shared_with_groups: Is graph shared with any groups?
		:param default_layout_id: Default layout of the graph
	"""

	# If graph already exists for user, alert them
	if db.get_graph(request.db_session, username, graphname) != None:
		raise Exception('Graph ' + graphname + ' already exists for ' + username + '!')

	validation_errors = validate_json(graph_json_string)
	if validation_errors is not None:
		raise Exception(validation_errors)

	graph_json = _load_graph_json(graph_json_string)

	# Construct new graph to add to database
	new_graph = db.add_graph(request.db_session, name=graphname, owner_email=username, json=json.dumps(graph_json, sort_keys=True, indent=4), is_public=public, default_layout_id=default_layout_id)
	add_graph_tags(request, new_graph.id, graph_json['metadata']['tags'] if 'tags' in graph_json['metadata'] else [])
	node_name_to_id_map = add_graph_nodes(request, new_graph.id, graph_json['graph']['nodes'])
	add_graph_edges(request, new_graph.id, graph_json['graph']['edges'], node_name_to_id_map)

	return new_graph


def add_graph_edges(request, graph_id, edges, node_name_to_id_map):
	dupEdges = []  # If there are edges with same source and directed
	rand = 0  # Number to differentiate between two duplicate edges

	for edge in edges:

		is_directed = 1  # Is the edge directed?

		# Make edge undirected if it doesn't have target_arrow_shape attribute
		if 'target_arrow_shape' not in edge['data']:
			edge['data']['target_arrow_shape'] = "none"
			is_directed = 0

		# To make sure int and floats are also accepted as source and target nodes of an edge
		source_node_id = str(node_name_to_id_map[str(edge['data']['source'])])
		target_node_id = str(node_name_to_id_map[str(edge['data']['target'])])


		# Keep track of all the duplicate edges
		# If there are two duplicate edges, append a counter and store it as an ID
		if source_node_id + '-' + target_node_id in dupEdges:
			rand += 1
			if 'id' not in edge['data']:
				edge['data']['id'] = source_node_id + '-' + target_node_id + rand
		# If this is first time we've seen an edge, simply get its ID without the counter
		else:
			if 'id' not in edge['data']:
				edge['data']['id'] = source_node_id + '-' + target_node_id

		dupEdges.append(source_node_id + '-' + target_node_id)

		# TRICKY NOTE: An edge's ID is used as the label property
		# The reason is because edge uses an 'id' column as the primary key.
		# The label was the column I decided to avoid completely reconstructing the database
		# POSSIBLE SOLUTION: If edge is bidirectional, we insert two edges with inverse source and target nodes

		db.add_edge(request.db_session, graph_id=graph_id, head_node_id=source_node_id, tail_node_id = target_node_id, name = edge['data']['id'], is_directed = is_directed)


def add_graph_nodes(request, graph_id, nodes):
	node_name_to_id_map = dict()
	for node in nodes:
		# Used for backwards-compatibility since some JSON have label
		# but new CytoscapeJS uses the content property
		if 'label' in node['data']:
			node['data']['content'] = node['data']['label']
			del node['data']['label']

		# If the node has any content inside of it, display that content, otherwise, just make it an empty string
		if 'content' not in node['data']:
			node['data']['content'] = ""

		# Add node to table
		new_node = db.add_node(request.db_session, name=node['data']['id'], label = node['data']['content'], graph_id = graph_id)

		node_name_to_id_map[new_node.name] = new_node.id
	return node_name_to_id_map


def add_graph_tags(request, graph_id, tags):
	for tag_name in tags:
		tag = db.get_tag_by_name(request.db_session, tag_name)
		tag_id = tag.id if tag is not None else db.add_tag(request.db_session, name=tag_name).id
		db.add_tag_to_graph(request.db_session, graph_id=graph_id, tag_id=tag_id)


def _load_graph_json(graph_json_string):
	graphJson = json.loads(graph_json_string) # Load JSON string into JSON structure

	# Needed for old graphs, converts CytoscapeWeb to CytoscapeJS standard
	if 'data' in graphJson['graph']:
		graphJson = json.loads(convert_json(graph_json_string))

	# Attach ID's to each edge for traversing the element
	graphJson = assign_edge_ids(graphJson)

	return graphJson


def _convert_order_query_term_to_database_order_object(order_query):
	"""
	It converts terms like owner_descending to desc(Graph.owner_email) which is readable by sqlalchemy.

	Parameters
	----------
	order_query: order query eg: owner_descending

	Returns
	-------
	order object like desc(Graph.owner_email)

	"""
	order_query = '' if order_query is None else order_query

	if 'owner' in order_query:
		attribute = db.Graph.owner_email
	elif 'graph' in order_query:
		attribute = db.Graph.name
	else:
		attribute = db.Graph.updated_at
	if 'ascending' in order_query:
		return db.asc(attribute)
	else:
		return db.desc(attribute)


def get_layout(request, layout_owner, layoutname, graph_id):
	# if there is no layout specified in the request (query term), then render the default layout
	# If there is a layout that is an automatic algorithm, simply return the default layout because the front-end JavaScript library handles the movement clientside
	graph = db.get_graph_by_id(request.db_session, graph_id)
	if layoutname is None or layoutname in AUTOMATIC_LAYOUT_ALGORITHMS or layout_owner is None:
		return graph.default_layout
	else:
		return db.get_layout(request.db_session, owner_email=layout_owner, name=layoutname, graph_id=graph_id)


def search_graphs_by_group_ids(request, group_ids=None, owner_email=None, names=None, nodes=None, edges=None, tags=None, limit=None, offset=None):
	if group_ids is None:
		raise Exception("Atleast one group id is required.")
	return db.find_graphs(request.db_session, group_ids=group_ids, owner_email=owner_email, names=names, nodes=nodes, edges=edges, tags=tags, limit=limit, offset=offset)


def add_graph_to_group(request, group_id, graph_id):
	if graph_id is not None:
		graph = db.get_graph_by_id(request.db_session, graph_id)
	else:
		raise Exception("Required Parameter is missing!")
	if graph is not None:
		return db.add_graph_to_group(request.db_session, group_id=group_id, graph_id=graph.id)
	else:
		raise Exception("Graph does not exit.")


def delete_graph_to_group(request, group_id, graph_id):
	db.delete_graph_to_group(request.db_session, group_id=int(group_id), graph_id=int(graph_id))
	return
