from datetime import datetime

from sqlalchemy.exc import IntegrityError

import applications.graphs.dal as db
import applications.users as users
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace_python.graphs.classes.gsgraph import GSGraph
from graphspace.wrappers import atomic_transaction
from graphspace_python.graphs.formatter.json_formatter import CyJSFormat
from applications.legend_formatter import convert_html_legend_1, convert_html_legend_2


import json
from json import dumps, loads

from django.conf import settings
from elasticsearch_dsl import Search, Q
from graphspace.data_type import DataType

AUTOMATIC_LAYOUT_ALGORITHMS = ['default_breadthfirst', 'default_concentric', 'default_circle', 'default_cose',
                               'default_grid']

HTML_LEGEND_TABLE_FORMAT_1 = 1
HTML_LEGEND_TABLE_FORMAT_2 = 2

def map_attributes(attributes):

	mapped_attributes = {}
	if attributes and isinstance(attributes, dict) and DataType.forValue(attributes) == DataType.DICT:
		for key, value in attributes.items():
			value_type = DataType.forValue(value)
			key_prefix = value_type.prefix()
			mapped_key = key_prefix + key if not key.startswith(key_prefix) else key
			if value_type == DataType.DICT:
				mapped_attributes[mapped_key] = map_attributes(value)
			else:
				mapped_attributes[mapped_key] = DataType.dateToStr(value, value_type)
	elif attributes and isinstance(attributes, list) and DataType.forValue(attributes) == DataType.DICT:
		return [map_attributes(item) for item in attributes]

	return mapped_attributes

def get_graph_by_id(request, graph_id):
	return db.get_graph_by_id(request.db_session, graph_id)

"""
Get the list of all graphs that is shared with a group
"""
def get_graphs_by_group(db_session, group_id):
	return db.get_graphs_by_group(db_session, group_id)

"""
Get a list of all users a specific graph is shared with
"""
def get_graphs_to_users(db_session, graph_id):
	return db.get_graphs_to_users(db_session, graph_id)


def is_user_authorized_to_view_graph(request, username, graph_id):
	is_authorized = False

	graph = db.get_graph_by_id(request.db_session, graph_id)

	if graph is not None:  # Graph doesnt exist
		if graph.owner_email == username:
			is_authorized = True
		elif graph.is_public == 1:  # graph is public
			is_authorized = True
		else:  # graph is not public
			for group in graph.groups:
				if users.controllers.is_member_of_group(request, username, group.id):
					is_authorized = True
	return is_authorized


def is_user_authorized_to_update_graph(request, username, graph_id):
	is_authorized = False
	user = users.controllers.get_user(request, username)

	graph = db.get_graph_by_id(request.db_session, graph_id)

	if graph is not None:  # Graph exists
		if graph.owner_email == username:
			is_authorized = True
		elif user is not None and user.is_admin == 1:
			is_authorized = True

	return is_authorized


def is_user_authorized_to_delete_graph(request, username, graph_id):
	is_authorized = False

	graph = db.get_graph_by_id(request.db_session, graph_id)

	if graph is not None:  # Graph exists
		if graph.owner_email == username:
			is_authorized = True

	return is_authorized


def is_user_authorized_to_share_graph(request, username, graph_id):
	is_authorized = False

	graph = db.get_graph_by_id(request.db_session, graph_id)

	if graph is not None:  # Graph exists
		if graph.owner_email == username:
			is_authorized = True
		elif graph.is_public == 1:  # graph is public
			is_authorized = True

	return is_authorized


def is_user_authorized_to_view_layout(request, username, layout_id):
	is_authorized = False

	layout = db.get_layout_by_id(request.db_session, layout_id)

	if layout is not None:  # Layout doesnt exists
		if layout.owner_email == username:
			is_authorized = True
		elif layout.is_shared == 1:  # layout is shared
			if get_graph_by_id(request, layout.graph_id).is_public == 1:
				is_authorized = True
			else:
				for group in layout.graph.groups:
					if users.controllers.is_member_of_group(request, username, group.id):
						is_authorized = True  # layout is shared with the user

	return is_authorized


def is_user_authorized_to_update_layout(request, username, layout_id):
	is_authorized = False

	layout = db.get_layout_by_id(request.db_session, layout_id)

	if layout is not None:  # Layout doesnt exists
		if layout.owner_email == username:
			is_authorized = True

	return is_authorized


def is_user_authorized_to_delete_layout(request, username, layout_id):
	is_authorized = False

	layout = db.get_layout_by_id(request.db_session, layout_id)

	if layout is not None:  # Layout doesnt exists
		if layout.owner_email == username:
			is_authorized = True

	return is_authorized


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
def add_graph(request, name=None, tags=None, is_public=None, graph_json=None, style_json=None, owner_email=None,
              default_layout_id=None):

	# If graph already exists for user, alert them
	if db.get_graph(request.db_session, owner_email, name) is not None:
		raise Exception('Graph ' + name + ' already exists for ' + owner_email + '!')

	if graph_json is not None:
		# TODO: add code to handle cyjs format
		G = CyJSFormat.create_gsgraph(json.dumps(graph_json))
		if style_json is not None:
			G.set_style_json(style_json)
		if name is not None:
			G.set_name(name)
		if tags is not None:
			G.set_tags(tags)

	owner_email = users.controllers.add_user(request).email if owner_email is None else owner_email

	# Construct new graph to add to database
	new_graph = db.add_graph(request.db_session, name=name, owner_email=owner_email,
	                         graph_json=json.dumps(G.get_graph_json()), style_json=json.dumps(G.get_style_json()),
	                         is_public=is_public, default_layout_id=default_layout_id)
	# Add graph tags
	for tag in G.get_tags():
		add_graph_tag(request, new_graph.id, tag)
	# Add graph nodes
	node_name_to_id_map = add_graph_nodes(request, new_graph.id, G.nodes(data=True))
	# Add graph edges
	edge_name_to_id_map = add_graph_edges(request, new_graph.id, G.edges(data=True), node_name_to_id_map)

	# Create json body to add into elasticsearch
	body_data = map_attributes(json.loads(new_graph.graph_json))
	body_data["string_owner_email"] = owner_email
	body_data["long_is_public"] = is_public
	body_data["datetime_updated_at"] = new_graph.updated_at
	settings.ELASTIC_CLIENT.index(index="graphs", doc_type='json', id=new_graph.id, body=body_data, refresh=True)

	return new_graph


@atomic_transaction
def update_graph(request, graph_id, name=None, is_public=None, graph_json=None, style_json=None, owner_email=None,
                 default_layout_id=None):
	graph = {}
	body_data = {} # JSON body that will be ued to update graph inElasticsearch
	if name is not None:
		graph['name'] = name
	if owner_email is not None:
		graph['owner_email'] = owner_email
		body_data['string_owner_email'] = owner_email
	if is_public is not None:
		graph['is_public'] = is_public
		body_data['long_is_public'] = is_public
	if default_layout_id is not None:
		graph['default_layout_id'] = default_layout_id if default_layout_id != 0 else None

	if style_json is not None:
		GSGraph.validate_style_json(style_json)
		graph['style_json'] = json.dumps(style_json)

	if graph_json is not None:
		G = CyJSFormat.create_gsgraph(json.dumps(graph_json))

		if name is not None:
			G.set_name(name)

		db.remove_nodes_by_graph_id(request.db_session, graph_id=graph_id)
		# Add graph nodes
		node_name_to_id_map = add_graph_nodes(request, graph_id, G.nodes(data=True))
		# Add graph edges
		edge_name_to_id_map = add_graph_edges(request, graph_id, G.edges(data=True), node_name_to_id_map)

		graph['graph_json'] = json.dumps(G.get_graph_json())

		body_data.update(map_attributes(G.get_graph_json()))

	updated_graph = db.update_graph(request.db_session, id=graph_id, updated_graph=graph)
	# If any information in Elasticsearch was changed
	if bool(body_data):
		body_data['datetime_updated_at'] = updated_graph.updated_at
		settings.ELASTIC_CLIENT.update(index="graphs", doc_type='json', id=graph_id, body={'doc': body_data}, refresh=True)

	return updated_graph


def get_graph_by_name(request, owner_email, name):
	return db.get_graph(request.db_session, owner_email=owner_email, name=name)

def delete_graph_by_id(request, graph_id):
	db.update_graph(request.db_session, id=graph_id, updated_graph={'default_layout_id': None})
	db.delete_graph(request.db_session, id=graph_id)
	settings.ELASTIC_CLIENT.delete(index="graphs", doc_type='json', id=graph_id, refresh=True)
	return


def add_graph_edges(request, graph_id, edges, node_name_to_id_map):
	edge_name_to_id_map = dict()
	for edge in edges:
		is_directed = 0 if 'is_directed' not in edge[2] or not edge[2]['is_directed'] else 1

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
		new_node = db.add_node(request.db_session, name=node[0], label=node[1]['label'], graph_id=graph_id)
		node_name_to_id_map[new_node.name] = new_node.id
	return node_name_to_id_map


def add_graph_tag(request, graph_id, tag_name):
	tag = db.get_tag_by_name(request.db_session, tag_name)
	tag_id = tag.id if tag is not None else db.add_tag(request.db_session, name=tag_name).id
	db.add_tag_to_graph(request.db_session, graph_id=graph_id, tag_id=tag_id)


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


def search_graphs_by_group_ids(request, group_ids=None, owner_email=None, names=None, nodes=None, edges=None, tags=None,
                               limit=None, offset=None):
	if group_ids is None:
		raise Exception("Atleast one group id is required.")
	return db.find_graphs(request.db_session, group_ids=group_ids, owner_email=owner_email, names=names, nodes=nodes,
	                      edges=edges, tags=tags, limit=limit, offset=offset)

"""
This function call will update the long_shared_users field in elasticsearch
whenever a user's access to a shared graph changes.
All we do is create a join of GroupsToGraphs and GroupsToUsers, and retrieve the new list of
users from postgres after it is updated. That is then used to update elasticsearch
"""
def update_shared_users_elasticsearch(request, graph_id):
	shared_users = [user.user_id for user in db.get_graphs_to_users(request.db_session, graph_id)]
	body_data = { 'long_shared_users': shared_users }
	settings.ELASTIC_CLIENT.update(index="graphs", doc_type='json', id=graph_id, body={'doc': body_data}, refresh=True)

def add_graph_to_group(request, group_id, graph_id):
	if graph_id is not None:
		graph = db.get_graph_by_id(request.db_session, graph_id)
	else:
		raise Exception("Required Parameter is missing!")
	if graph is not None:
		result = db.add_graph_to_group(request.db_session, group_id=group_id, graph_id=graph.id)
		update_shared_users_elasticsearch(request, graph_id) # Update elasticsearch also before returning
		return result
	else:
		raise Exception("Graph does not exit.")

def delete_graph_to_group(request, group_id, graph_id):
	db.delete_graph_to_group(request.db_session, group_id=int(group_id), graph_id=int(graph_id))
	update_shared_users_elasticsearch(request, graph_id) # Update elasticsearch also before returning
	return

def search_graphs1(request, owner_email=None, names=None, nodes=None, edges=None, tags=None, member_email=None,
                   is_public=None, query=None, limit=20, offset=0, order='desc', sort='name'):
	is_public = int(is_public) if is_public is not None else None

	if member_email is not None:
		member_user = users.controllers.get_user(request, member_email)
		if member_user is None:
			raise Exception("User with given member_email doesnt exist.")
	else:
		member_user = None

	# Edge searching currently not enabled
	if edges is not None:
		edges = [tuple(edge.split(':')) for edge in edges]

	# Querying only elasticsearch. No need to go to postgres since ES has all required data

	# This maps the field names from postgres to the field names in Elasticsearch.
	# Needed for the 'sort' paramter in the query that goes into ES
	postgres_to_elasticsearch_mapping = {
		"name":"object_data.string_name.keyword",
		"owner_email": "string_owner_email.keyword",
		"is_public": "long_is_public",
		"updated_at": "datetime_updated_at"
	}

	# Creating the query to send to Elasticsearch. Note that we no longer query
	# postgres. All required data is stored in Elasticearch
	query["size"] = limit
	query["from"] = offset
	query["_source"] = [	# Select fields to get from Elasticsearch
		"string_owner_email", "long_is_public", "object_data.string_name",
		"object_data.string_tags", "datetime_updated_at"
	]
	query["sort"] = [{	# Results need to be sorted
		postgres_to_elasticsearch_mapping[sort] : {"order": order}
	}]
	added_query = {}

	if owner_email != None:  # My Graphs
		added_query["query"] = "(string_owner_email:\"" + owner_email + "\")"
	elif member_email != None: # Shared Graphs
		added_query["query"] = "(long_shared_users: " + str(member_user.id) + ")"
	elif is_public != None:  # Public Graphs
		added_query["query"] = "(long_is_public:" + str(is_public) + ")"

	if 'query' in query:
		# Search parameter has been provided
		query["query"]["bool"]["must"].append({
			"query_string": added_query		# filter by owner_email or is_public
		})
		query["query"]["bool"]["minimum_should_match"] = 1

	else:
		# No search paramter. Must list all graphs
		query["query"] = {}
		query["query"]["bool"] = {}
		query["query"]["bool"]["must"] = []
		query["query"]["bool"]["must"].append({
			"query_string": added_query		# filter by owner_email or is_public
		})
		query["query"]["bool"]["minimum_should_match"] = 0

	# Query elasticsearch once
	s = Search(using=settings.ELASTIC_CLIENT, index='graphs')
	s.update_from_dict(query)
	response = s.execute()

	#Creating an array of graphs as JSON objects
	graphs_list = []
	for hit in s:
		if 'string_tags' not in hit.object_data:
			hit.object_data.string_tags = [] # tags may be empty!
		graphs_list.append({
			"name": hit.object_data.string_name,
			"tags": [tag for tag in hit.object_data.string_tags],
			"is_public": hit.long_is_public,
			"owner_email": hit.string_owner_email,
			"id": hit.meta.id,
			"updated_at": hit.datetime_updated_at
		})

	return response.hits.total, graphs_list

def search_graphs(request, owner_email=None, member_email=None, names=None, is_public=None, nodes=None, edges=None,
                  tags=None, limit=20, offset=0, order='desc', sort='name'):
	sort_attr = getattr(db.Graph, sort if sort is not None else 'name')
	orber_by = getattr(db, order if order is not None else 'desc')(sort_attr)
	is_public = int(is_public) if is_public is not None else None

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

	# if names is not None and len(names) > 0:
	# 	s = Search(using=settings.ELASTIC_CLIENT, index='graphs').query("match", **{"object_data.string_name": "kegg"})
	# 	query = {
	# 		"query": {
	# 			"bool": {
	# 				"should": [
	# 					{
	# 						"query_string": {
	# 							"default_field" : "object_data.string_name",
	# 							"query": ' OR '.join([name.replace('%', '*') for name in names])
	# 						}
	# 					}
	# 				]
	# 			}
	# 		}
	# 	}
	# 	s.update_from_dict(query)
	# 	s.source(False)
	# 	graph_ids = [int(hit.meta.id) for hit in s.scan()]
	# else:
	# 	graph_ids=None

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


def search_layouts(request, owner_email=None, is_shared=None, name=None, graph_id=None, limit=20, offset=0,
                   order='desc', sort='name'):
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
	                                 is_shared=is_shared,
	                                 name=name,
	                                 graph_id=graph_id,
	                                 limit=limit,
	                                 offset=offset,
	                                 order_by=orber_by)

	return total, layouts


def get_layout_by_id(request, layout_id):
	return db.get_layout_by_id(request.db_session, layout_id)


def add_layout(request, owner_email=None, name=None, graph_id=None, is_shared=None, style_json=None,
               positions_json=None):
	if name is None or owner_email is None or graph_id is None:
		raise Exception("Required Parameter is missing!")
	try:
		return db.add_layout(request.db_session, owner_email=owner_email, name=name, graph_id=graph_id,
		                     is_shared=is_shared, style_json=dumps(style_json), positions_json=dumps(positions_json))
	except IntegrityError as e:
		raise BadRequest(request, error_code=ErrorCodes.Validation.LayoutNameAlreadyExists, args=name)


def update_layout(request, layout_id, owner_email=None, name=None, graph_id=None, is_shared=None, style_json=None,
                  positions_json=None):
	if layout_id is None:
		raise Exception("Required Parameter is missing!")

	layout = {}
	if name is not None:
		layout['name'] = name
	if owner_email is not None:
		layout['owner_email'] = owner_email
	if graph_id is not None:
		layout['graph_id'] = graph_id
	if is_shared is not None:
		layout['is_shared'] = is_shared
	if style_json is not None:
		layout['style_json'] = dumps(style_json)
	if positions_json is not None:
		layout['positions_json'] = dumps(positions_json)

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


def search_edges(request, is_directed=None, names=None, edges=None, graph_id=None, limit=20, offset=0, order='desc',
                 sort='name'):
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
	return db.add_edge(request.db_session, name=name, head_node_id=head_node_id, tail_node_id=tail_node_id,
	                   is_directed=is_directed, graph_id=graph_id)


def delete_edge_by_id(request, edge_id):
	db.delete_edge(request.db_session, id=edge_id)
	return


def convert_html_legend(graph_json, style_json, param):
	if param['update_legend_format'] == HTML_LEGEND_TABLE_FORMAT_1:
		return convert_html_legend_1(graph_json, style_json)

	if param['update_legend_format'] == HTML_LEGEND_TABLE_FORMAT_2:
		return convert_html_legend_2(graph_json, style_json)


def update_graph_with_html_legend(request, graph_id, param):
	graph = db.get_graph_by_id(request.db_session, graph_id)
	style_json = json.loads(graph.style_json)
	graph_json = json.loads(graph.graph_json)
	updated_style_json = convert_html_legend(graph_json=graph_json,  style_json=style_json, param=param)
	del graph_json["data"]["description"]
	return update_graph(request, graph_id=graph_id, style_json=updated_style_json, graph_json=graph_json)
