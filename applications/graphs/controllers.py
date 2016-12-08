from datetime import datetime

import applications.graphs.dal as db
import applications.users as users
from graphspace.wrappers import atomic_transaction
from json_validator import *
from graphspace.fileformat import GraphSpaceJSONFormat
import networkx as nx
from json import dumps, loads

AUTOMATIC_LAYOUT_ALGORITHMS = ['default_breadthfirst', 'default_concentric', 'default_circle', 'default_cose',
							   'default_grid']


def get_graph(request, graph_owner, graphname):
	graph = db.get_graph(request.db_session, graph_owner,
						 graphname) if graphname is not None and graph_owner is not None else None
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

		return db.get_graphs_by_edges_and_nodes_and_names(request.db_session,
														  group_ids=[group.id for group in user.member_groups],
														  names=filter(None, names), nodes=filter(None, nodes),
														  edges=edges, page=page, page_size=page_size,
														  partial_matching=True if search_type == 'partial_search' else False,
														  order=_convert_order_query_term_to_database_order_object(
															  order_by), tags=tags)


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

		return db.get_graphs_by_edges_and_nodes_and_names(request.db_session, owner_email=uid,
														  names=filter(None, names), nodes=filter(None, nodes),
														  edges=edges, page=page, page_size=page_size,
														  partial_matching=True if search_type == 'partial_search' else False,
														  order=_convert_order_query_term_to_database_order_object(
															  order_by), tags=tags)


def search_public_graphs(request, uid, search_type, search_terms, tags, order_by, page, page_size):
	edges, nodes, names = [], [], []
	for term in search_terms:
		if ':' in term:
			edges.append(term)
		else:
			names.append(term)
			nodes.append(term)

	return db.get_graphs_by_edges_and_nodes_and_names(request.db_session, is_public=1, names=filter(None, names),
													  nodes=filter(None, nodes), edges=edges, page=page,
													  page_size=page_size,
													  partial_matching=True if search_type == 'partial_search' else False,
													  order=_convert_order_query_term_to_database_order_object(
														  order_by), tags=tags)


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
def add_graph(request, name=None, tags=None, is_public=None, json_graph=None, cyjs_graph=None, owner_email=None,
			  default_layout_id=None):
	# If graph already exists for user, alert them
	if db.get_graph(request.db_session, owner_email, name) is not None:
		raise Exception('Graph ' + name + ' already exists for ' + owner_email + '!')

	if json_graph is not None:
		G = GraphSpaceJSONFormat.create_gsgraph(json.dumps(json_graph))
		if name is not None:
			G.set_name(name)
		if tags is not None:
			G.set_tags(tags)
	else:
		# TODO: add code to handle cyjs format
		pass

	owner_email = users.controllers.add_user(request).email if owner_email is None else owner_email

	# Construct new graph to add to database
	new_graph = db.add_graph(request.db_session, name=name, owner_email=owner_email, json=json.dumps(G.get_json()),
							 is_public=is_public, default_layout_id=default_layout_id)
	# Add graph tags
	for tag in G.get_tags():
		add_graph_tag(request, new_graph.id, tag)
	# Add graph nodes
	node_name_to_id_map = add_graph_nodes(request, new_graph.id, G.nodes(data=True))
	# Add graph edges
	edge_name_to_id_map = add_graph_edges(request, new_graph.id, G.edges(data=True), node_name_to_id_map)

	nx.set_node_attributes(G, 'nodeId', node_name_to_id_map)
	nx.set_edge_attributes(G, 'edgeId', edge_name_to_id_map)
	new_graph = db.update_graph(request.db_session, id=new_graph.id, updated_graph={
		'json': json.dumps(G.compute_json())
	})

	return new_graph


@atomic_transaction
def update_graph(request, graph_id, name=None, is_public=None, json_string=None, owner_email=None,
				 default_layout_id=None):
	graph = {}
	if name is not None:
		graph['name'] = name
	if owner_email is not None:
		graph['owner_email'] = owner_email
	if is_public is not None:
		graph['is_public'] = is_public
	if default_layout_id is not None:
		graph['default_layout_id'] = default_layout_id

	if json_string is not None:
		G = GraphSpaceJSONFormat.create_gsgraph(json.dumps(json_string))
		if name is not None:
			G.set_name(name)

		db.remove_nodes_by_graph_id(request.db_session, graph_id=graph_id)
		# Add graph nodes
		node_name_to_id_map = add_graph_nodes(request, graph_id, G.nodes(data=True))
		# Add graph edges
		edge_name_to_id_map = add_graph_edges(request, graph_id, G.edges(data=True), node_name_to_id_map)
		nx.set_node_attributes(G, 'nodeId', node_name_to_id_map)
		nx.set_edge_attributes(G, 'edgeId', edge_name_to_id_map)
		graph['json'] = json.dumps(G.compute_json())

	return db.update_graph(request.db_session, id=graph_id, updated_graph=graph)


def delete_graph_by_id(request, graph_id):
	db.delete_graph(request.db_session, id=graph_id)
	return


def add_graph_edges(request, graph_id, edges, node_name_to_id_map):
	edge_name_to_id_map = dict()
	for edge in edges:
		# Make edge undirected if its target_arrow_shape attribute is set to none
		is_directed = 0 if edge[2]['target_arrow_shape'] == 'none' else 1

		# To make sure int and floats are also accepted as source and target nodes of an edge
		new_edge = db.add_edge(request.db_session, graph_id=graph_id, head_node_id=str(node_name_to_id_map[edge[1]]),
							   tail_node_id=str(node_name_to_id_map[edge[0]]), name=str(edge[2]['name']),
							   is_directed=is_directed)
		edge_name_to_id_map[(edge[0], edge[1])] = new_edge.id
	return edge_name_to_id_map


def add_graph_nodes(request, graph_id, nodes):
	node_name_to_id_map = dict()
	for node in nodes:
		# Add node to table
		new_node = db.add_node(request.db_session, name=node[0], label=node[1]['content'], graph_id=graph_id)
		node_name_to_id_map[new_node.name] = new_node.id
	return node_name_to_id_map


def add_graph_tag(request, graph_id, tag_name):
	tag = db.get_tag_by_name(request.db_session, tag_name)
	tag_id = tag.id if tag is not None else db.add_tag(request.db_session, name=tag_name).id
	db.add_tag_to_graph(request.db_session, graph_id=graph_id, tag_id=tag_id)


def _validate_and_load_graph_json(graph_json_string):
	clean_json, validation_errors = validate_clean_json(graph_json_string)

	if validation_errors is not None:
		raise Exception(validation_errors)

	return clean_json


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


def search_graphs_by_group_ids(request, group_ids=None, owner_email=None, names=None, nodes=None, edges=None, tags=None,
							   limit=None, offset=None):
	if group_ids is None:
		raise Exception("Atleast one group id is required.")
	return db.find_graphs(request.db_session, group_ids=group_ids, owner_email=owner_email, names=names, nodes=nodes,
						  edges=edges, tags=tags, limit=limit, offset=offset)


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


def search_graphs(request, owner_email=None, member_email=None, names=None, is_public=None, nodes=None, edges=None,
				  tags=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'name':
		sort_attr = db.Graph.name
	elif sort == 'update_at':
		sort_attr = db.Graph.updated_at
	elif sort == 'owner_email':
		sort_attr = db.Graph.owner_email
	else:
		sort_attr = db.Graph.name

	if order == 'desc':
		orber_by = db.desc(sort_attr)
	else:
		orber_by = db.asc(sort_attr)

	if is_public is True:
		is_public = 1
	elif is_public is False:
		is_public = 0

	if member_email is not None:
		member_user = users.controllers.get_user(request, member_email)
		if member_user is not None:
			group_ids = [group.id for group in users.controllers.get_groups_by_member_id(request, member_user.id)]
		else:
			raise Exception("User with given member_email doesnt exist.")
	else:
		group_ids = None
	if edges is not None:
		edges = [tuple(edge.split(':')) for edge in edges]

	total, graphs_list = db.find_graphs(request.db_session,
										owner_email=owner_email,
										names=names,
										is_public=is_public,
										group_ids=group_ids,
										nodes=nodes,
										edges=edges,
										tags=tags,
										limit=limit,
										offset=offset,
										order_by=orber_by)

	return total, graphs_list


def search_layouts(request, owner_email=None, name=None, graph_id=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'name':
		sort_attr = db.Layout.name
	elif sort == 'update_at':
		sort_attr = db.Layout.updated_at
	elif sort == 'owner_email':
		sort_attr = db.Layout.owner_email
	else:
		sort_attr = db.Layout.name

	if order == 'desc':
		orber_by = db.desc(sort_attr)
	else:
		orber_by = db.asc(sort_attr)

	total, layouts = db.find_layouts(request.db_session,
										owner_email=owner_email,
										name=name,
										graph_id=graph_id,
										limit=limit,
										offset=offset,
										order_by=orber_by)

	return total, layouts


def get_layout_by_id(request, layout_id):
	return db.get_layout_by_id(request.db_session, layout_id)


def add_layout(request, owner_email=None, name=None, graph_id=None, is_public=None, is_shared_with_groups=None, json=None):
	if name is None or owner_email is None or graph_id is None:
		raise Exception("Required Parameter is missing!")
	return db.add_layout(request.db_session, owner_email=owner_email, name=name, graph_id=graph_id, is_public=is_public, is_shared_with_groups=is_shared_with_groups, json=dumps(json))


def update_layout(request, layout_id, owner_email=None, name=None, graph_id=None, is_public=None, is_shared_with_groups=None, json=None):
	if layout_id is None:
		raise Exception("Required Parameter is missing!")

	layout = {}
	if name is not None:
		layout['name'] = name
	if owner_email is not None:
		layout['owner_email'] = owner_email
	if graph_id is not None:
		layout['graph_id'] = graph_id
	if is_public is not None:
		layout['is_public'] = is_public
	if is_shared_with_groups is not None:
		layout['is_shared_with_groups'] = is_shared_with_groups
	if json is not None:
		layout['json'] = dumps(json)

	return db.update_layout(request.db_session, id=layout_id, updated_layout=layout)


def delete_layout_by_id(request, layout_id):
	db.delete_layout(request.db_session, id=layout_id)
	return


def search_nodes(request, graph_id=None, names=None, labels=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'name':
		sort_attr = db.Node.name
	elif sort == 'update_at':
		sort_attr = db.Node.updated_at
	elif sort == 'label':
		sort_attr = db.Node.label
	else:
		sort_attr = db.Node.name

	if order == 'desc':
		orber_by = db.desc(sort_attr)
	else:
		orber_by = db.asc(sort_attr)

	## TODO: create a util function to relpace the code parse sort and order parameters. This code is repeated again and again.

	total, nodes = db.find_nodes(request.db_session,
										names=names,
										labels=labels,
										graph_id=graph_id,
										limit=limit,
										offset=offset,
										order_by=orber_by)

	return total, nodes


def get_node_by_id(request, node_id):
	return db.get_node_by_id(request.db_session, node_id)


def add_node(request, name=None, label=None, graph_id=None):
	if name is None or graph_id is None:
		raise Exception("Required Parameter is missing!")
	return db.add_node(request.db_session, name=name, label=label, graph_id=graph_id)


def delete_node_by_id(request, node_id):
	db.delete_node(request.db_session, id=node_id)
	return


def search_edges(request, is_directed=None, names=None, edges=None, graph_id=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'name':
		sort_attr = db.Edge.name
	elif sort == 'update_at':
		sort_attr = db.Edge.updated_at
	else:
		sort_attr = db.Edge.name

	if order == 'desc':
		orber_by = db.desc(sort_attr)
	else:
		orber_by = db.asc(sort_attr)

	if edges is not None:
		edges = [tuple(edge.split(':')) for edge in edges]

	## TODO: create a util function to relpace the code parse sort and order parameters. This code is repeated again and again.

	total, edges = db.find_edges(request.db_session,
										names=names,
										edges=edges,
										is_directed=is_directed,
										graph_id=graph_id,
										limit=limit,
										offset=offset,
										order_by=orber_by)

	return total, edges


def get_edge_by_id(request, edge_id):
	return db.get_edge_by_id(request.db_session, edge_id)


def add_edge(request, name=None, head_node_id=None, tail_node_id=None, is_directed=0, graph_id=None):
	if name is None or graph_id is None or head_node_id is None or tail_node_id is None:
		raise Exception("Required Parameter is missing!")
	return db.add_node(request.db_session, name=name, head_node_id=head_node_id, tail_node_id=tail_node_id, is_directed=is_directed, graph_id=graph_id)

def delete_edge_by_id(request, edge_id):
	db.delete_edge(request.db_session, id=edge_id)
	return
