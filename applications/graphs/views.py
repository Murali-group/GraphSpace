import json

import applications.graphs.controllers as graphs
import applications.users.controllers as users
import graphspace.utils as utils
from applications.graphs.forms import SearchForm
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.shortcuts import render
from django.template import RequestContext


def upload_graph_page(request):
	context = RequestContext(request, {})

	if request.method == 'POST':
		try:
			if str(request.FILES['graph_file']).endswith("json"):
				graph = add_graph(request, graph={
					'name': request.POST.get('name', None),
					'owner_email': request.POST.get('owner_email', None),
					'is_public': request.POST.get('is_public', None),
					'json': json.loads(request.FILES['graph_file'].read()),
				})
			else:
				graph = add_graph(request, graph={
					'name': request.POST.get('name', None),
					'owner_email': request.POST.get('owner_email', None),
					'is_public': request.POST.get('is_public', None),
					'cyjs': json.loads(request.FILES['graph_file'].read()),
				})

			context['Success'] = settings.URL_PATH + "graphs/" + str(graph['id'])
		except Exception as e:
			context['Error'] = str(e)

		return render(request, 'graphs/upload_graph.html', context)
	else:
		return render(request, 'graphs/upload_graph.html', context)


def view_graph(request, graph_owner, graphname):
	"""
		View a graph with CytoscapeJS.

		:param request: HTTP GET Request
		:param graph_owner: Owner of the graph to view
		:param graphname: Graph name of the graph to view
	"""
	context = RequestContext(request)
	graphname = graphname.strip('/')
	layoutname = request.GET.get('layout') if len(request.GET.get('layout', '')) > 0 else None
	layout_owner = request.GET.get('layout_owner') if len(request.GET.get('layout_owner', '')) > 0 else None

	try:
		graph = graphs.get_graph(request, graph_owner, graphname)

		if graph is None:
			raise Exception(
				"Graph: " + graphname + " does not exist for " + graph_owner + ".  Upload a graph with this name into GraphSpace in order to see it.")

		if not graphs.is_user_authorized_to_view_graph(request, request.session['uid'], graph.id):
			raise Exception(
				"You are not authorized to view this graph, create an account and contact graph's owner for permission to see this graph.")

		layout = graphs.get_layout(request, layout_owner, layoutname, graph.id)

		if layout is None:
			if "layout" in request.GET and layoutname not in graphs.AUTOMATIC_LAYOUT_ALGORITHMS:
				raise Exception("Layout: " + request.GET.get(
					'layout') + " does not exist.  Click <a href='" + settings.URL_PATH + "graphs/" + graph_owner + "/" + graphname + "'>here</a> to view this graph without the specified layout.")
		elif layout.is_public != 1 and layout.is_shared != 1:
			raise Exception(layout.owner_email + " has not shared " + request.GET.get(
				'layout') + " layout yet.  Click <a href='" + settings.URL_PATH + "graphs/" + graph_owner + "/" + graphname + "'>here</a> to view this graph without the specified layout.")
		else:
			context['default_layout_name'] = graph.default_layout.name
			context['default_layout'] = utils.cytoscapePresetLayout(json.dump(graph.default_layout.json))
			context['layout_name'] = layout.name
			context['layout_to_view'] = utils.cytoscapePresetLayout(json.dump(layout.json))
			context['layout_urls'] = settings.URL_PATH + "graphs/" + graph_owner + "/" + graphname + "?layout="
			context["layout_owner"] = layout.owner_email

			# If user is logged in, display my layouts and shared layouts
			if request.session['uid'] is not None:

				context['my_layouts'] = []
				context['shared_layouts'] = graph.layouts
				context['my_shared_layouts'] = []

				for layout in graph.layouts:
					if layout.is_shared_with_groups == 0 and layout.is_public == 0:
						context['my_layouts'].append(layout)
						context['my_shared_layouts'].append(layout)

		context["graph"] = _convert_to_cytoscape_json(graph.json)
		context['draw_graph'] = True
		context['shared_groups'] = [(group.name, group.owner_email) for group in graph.groups]
		context['shared'] = 'Publicly Shared' if graph.is_public else 'Privately Shared'

		json_data = json.loads(context['graph'])
		if 'description' in json_data['metadata']:
			context['description'] = json_data['metadata']['description'] + "</table></html>"
		else:
			context['description'] = ""

		context['owner'] = graph_owner

		# If the metadata has either a name or a title (backward-compatible)
		# display it on the top of the graph
		if 'name' in json_data['metadata']:
			context['graph_name'] = json_data['metadata']['name']
		elif 'title' in json_data['metadata']:
			context['graph_name'] = json_data['metadata']['title']
		else:
			context['graph_name'] = ''

		# graph id
		context['graph_id'] = graphname

		if len(json_data['graph']['edges']) > 0 and 'k' in json_data['graph']['edges'][0]['data']:
			context['filters'] = True

		# redirect if the user wishes to view the json data
		if request.method == "GET" and 'view_json' in request.GET:
			return HttpResponseRedirect("/json/%s/%s" % (graph_owner, graphname))

		context['draw_graph'] = True
		# Don't display the task_view
		context["task_view"] = False
		context["approve_view"] = False
		context["researcher_view"] = True

		return render(request, 'graphs/view_graph.html', context)

	except Exception as e:
		context['Error'] = str(e)
		return render(request, 'graphs/error.html', context)


def _convert_to_cytoscape_json(graphjson):
	"""
		Converts JSON to CytoscapeJS standards

		:param graphjson: JSON of graph to render on CytoscapeJS
		:return JSON: CytoscapeJS-compatible graphname
	"""

	temp_json = json.loads(graphjson)['graph']

	# for Cytoscape.js, if data is in properties, then we need to convert (main difference)
	if 'data' in temp_json:
		return convert_json(graphjson)
	else:
		return graphjson


def graphs_page(request):
	"""
		Wrapper view for the graphs page.

		:param request: HTTP GET Request.
	"""
	context = RequestContext(request, {})
	uid = request.session['uid'] if 'uid' in request.session else None
	try:
		context.push({
			"public_graphs": get_graphs(request, query={'is_public': True}),
		})
		if uid is not None:
			context.push({
				"owned_graphs": get_graphs(request, query={'owner_email': uid}),
				"shared_graphs": get_graphs(request, query={'member_email': uid})
			})

		if request.META.get('HTTP_ACCEPT', None) == 'application/json':
			return HttpResponse(json.dumps(context.dicts), content_type="application/json")
		else:
			return render(request, 'graphs/graphs.html', context)
	except Exception as e:
		context['Error'] = str(e)
		return render(request, 'graphs/error.html', context)


def get_graphs(request, query=dict()):
	"""
	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the graphs.
	name: string
		name of the graphs are shared with.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	is_public: boolean
		Search for graphs with given visibility. In order to search for public graphs set is_public to True.
		In order to search for private graphs set is_public to False. In order to search for all graphs set is_public to None.
	names : list of strings
		Search for graphs with given list of names. In order to search for graphs with given name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all graphs with xyz in their name.
	nodes : list of strings
		Search for graphs with given given list of node names. In order to search for graphs with given node name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all graphs with xyz in their node name.
	edges : list of strings
		Search for graphs with the edge between given given list of node names separated by colon. In order to search for graphs with given edge as a substring, wrap the name of the nodes with percentage symbol. For example, %xyz%:%abc% will search for all graphs with edge between nodes with 'xyz' and 'abc' in their node names.
	tags : list of strings
		Search for graphs with the given given list of tag names. In order to search for graphs with given tag as a substring, wrap the name of the tag with percentage symbol. For example, %xyz% will search for all graphs with 'xyz' in their tag names.
	order : string
		Defines the column sort order, can only be 'asc' or 'desc'.
	sort : string
		Defines which column will be sorted.

	Parameters
	----------
	query : dict
		Dictionary of query parameters.
	request : object
		HTTP GET Request.
	owner_email : string
		Email of the Owner of the groups.

	Returns
	-------
	total : integer
		Number of groups matching the request.
	groups : List of Groups.
		List of Group Objects with given limit and offset.

	Raises
	------

	Notes
	------
	"""

	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	total, graphs_list = graphs.search_graphs(request,
											  owner_email=query.get('owner_email', None),
											  member_email=query.get('member_email', None),
											  names=list(filter(None, query.getlist('names[]', []))),
											  is_public=query.get('is_public', None),
											  nodes=list(filter(None, query.getlist('nodes[]', []))),
											  edges=list(filter(None, query.getlist('edges[]', []))),
											  tags=list(filter(None, query.getlist('tags[]', []))),
											  limit=query.get('limit', 20),
											  offset=query.get('offset', 0),
											  order=query.get('order', 'desc'),
											  sort=query.get('sort', 'name'))

	return {
		'total': total,
		'graphs': [utils.serializer(graph) for graph in graphs_list]
	}


def get_graph(request, graph_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	graph_id : string
		Unique ID of the graph.

	Returns
	-------
	graph: object

	Raises
	------

	Notes
	------

	"""
	return utils.serializer(graphs.get_graph_by_id(request, graph_id))


def add_graph(request, graph={}):
	"""
	Graph Parameters
	----------
	name : string
		Name of group. Required
	owner_email : string
		Email of the Owner of the graph. Required
	tags: list of strings
		List of tags to be attached with the graph. Optional


	Parameters
	----------
	graph : dict
		Dictionary containing the data of the graph being added.
	request : object
		HTTP POST Request.

	Returns
	-------
	graph : object
		Newly created graph object.

	Raises
	------

	Notes
	------

	"""

	return utils.serializer(graphs.add_graph(request,
											 name=graph.get('name', None),
											 is_public=graph.get('is_public', None),
											 json_graph=graph.get('json', None),
											 cyjs_graph=graph.get('cyjs', None),
											 tags=graph.get('tags', None),
											 owner_email=graph.get('owner_email', None)))


def update_graph(request, graph_id, graph={}):
	"""
	Graph Parameters
	----------
	name : string
		Name of group. Required
	owner_email : string
		Email of the Owner of the graph. Required


	Parameters
	----------
	graph_id : string
		Unique ID of the graph.
	graph : dict
		Dictionary containing the data of the graph being added.
	request : object
		HTTP POST Request.

	Returns
	-------
	graph : object
		Updated graph object.

	Raises
	------

	Notes
	------

	"""

	return utils.serializer(graphs.update_graph(request,
												graph_id=graph_id,
												name=graph.get('name', None),
												is_public=graph.get('is_public', None),
												json_string=graph.get('json', None),
												owner_email=graph.get('owner_email', None),
												default_layout_id=graph.get('default_layout_id', None)))


def delete_graph(request, graph_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	graph_id : string
		Unique ID of the graph.

	Returns
	-------
	None

	Raises
	------

	Notes
	------

	"""
	graphs.delete_graph_by_id(request, graph_id)


def gs_graphs(request, graph_id=None):
	"""
	Handles any request (GET/POST) sent to /graphs or graphs/<graph_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if request.method == "GET" and graph_id is None:
				return HttpResponse(json.dumps(get_graphs(request, query=request.GET)), content_type="application/json")
			elif request.method == "GET" and graph_id is not None:
				return HttpResponse(json.dumps(get_graph(request, graph_id)), content_type="application/json",
									status=200)
			elif request.method == "POST" and graph_id is None:
				return HttpResponse(json.dumps(add_graph(request, graph=json.loads(request.body))),
									content_type="application/json", status=201)
			elif request.method == "PUT" and graph_id is not None:
				return HttpResponse(json.dumps(update_graph(request, graph_id, graph=json.loads(request.body))),
									content_type="application/json",
									status=200)
			elif request.method == "DELETE" and graph_id is not None:
				delete_graph(request, graph_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted graph with id=%s" % graph_id
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def graph_page(request, graph_id):
	"""
		Wrapper view for the group page. /graphs/<graph_id>

		:param request: HTTP GET Request.

	Parameters
	----------
	graph_id : string
		Unique ID of the graph. Required
	"""
	context = RequestContext(request, {})
	uid = request.session['uid'] if 'uid' in request.session else None
	if uid is not None:
		context.push({
			"graph": get_graph(request, graph_id),
			"groups": [utils.serializer(group) for group in
					   users.get_groups_by_member_id(request, member_id=users.get_user(request, uid).id)],
			"shared_groups": get_graph_groups(request, graph_id, query={'limit': None,'offset': None})['groups'],
			"layouts": get_layouts(request, query={"graph_id": graph_id, 'limit': None, 'offset': None})['layouts']
		})
		context['graph_json_string'] = json.dumps(context['graph']['json'])
		shared_group_ids = [group['id'] for group in context["shared_groups"]]
		for group in context['groups']:
			group['is_shared'] = 1 if group['id'] in shared_group_ids else 0

		if request.META.get('HTTP_ACCEPT', None) == 'application/json':
			return HttpResponse(json.dumps(context.dicts), content_type="application/json")
		else:
			return render(request, 'graphs/graph.html', context)
	else:
		context[
			'Error'] = "You are not authorized to view this graph, create an account and contact graph's owner for permission to see this graph.!"
		return render(request, 'graphs/error.html', context)


def graph_groups(request, graph_id, group_id=None):
	"""
	Handles any request (GET/POST) sent to graphs/<graph_id>/groups or graphs/<graph_id>/groups/<group_id>.

	Parameters
	----------
	request - HTTP Request
	graph_id : string
		Unique ID of the graph.

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if graph_id is None:
				raise Exception("Graph ID is required.")

			if request.method == "GET" and group_id is None:
				return HttpResponse(json.dumps(get_graph_groups(request, graph_id, query=request.GET)),
									content_type="application/json")
			elif request.method == "POST" and group_id is None:
				return HttpResponse(json.dumps(add_graph_group(request, graph_id, group=json.loads(request.body))), content_type="application/json",
									status=201)
			elif request.method == "DELETE" and group_id is not None:
				delete_graph_group(request, graph_id, group_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted graph with id=%s from group with id=%s" % (graph_id, group_id)
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def add_graph_group(request, graph_id, group={}):
	"""
	Body Parameters
	----------
	group_id : string
		Unique ID of the group.

	Parameters
	----------
	request : object
		HTTP POST Request.

	graph_id : string
		User ID of the member. Required

	Returns
	-------
	group_to_graph : object
		Newly added group_to_graph relationship.

	Raises
	------

	Notes
	------
	"""

	return utils.serializer(users.add_group_graph(request,
												  graph_id=graph_id,
												  group_id=group.get('group_id', None)))


def delete_graph_group(request,  graph_id, group_id):
	"""
	Parameters
	----------
	request : object
		HTTP POST Request.
	group_id : string
		Unique ID of the group. Required
	graph_id : string
		User ID of the member. Required


	Returns
	-------
	None.

	Raises
	------

	Notes
	------
	"""
	users.delete_group_graph(request,
							 group_id=group_id,
							 graph_id=graph_id)


def get_graph_groups(request, graph_id, query={}):
	"""

	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the groups.
	member_email: string
		Email of the member of the groups.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	name : string
		Search for groups with given name. In order to search for groups with given name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all groups with xyz in their name.
	description : string
		Search for groups with given description. In order to search for groups with given description as a substring, wrap the description with percentage symbol. For example, %xyz% will search for all groups with xyz in their description.
	order : string
		Defines the column sort order, can only be 'asc' or 'desc'.
	sort : string
		Defines which column will be sorted.


	Parameters
	----------
	request : object
		HTTP GET Request.
	graph_id : string
		Unique ID of the graph.

	Returns
	-------
	total : integer
		Number of groups matching the request.
	groups : List of Groups.
		List of Group Objects with given limit and offset.

	Raises
	------

	Notes
	------

	"""
	total, groups = users.search_groups(request,
										graph_ids=[graph_id],
										owner_email=query.get('owner_email', None),
										member_email=query.get('member_email', None),
										name=query.get('name', None),
										description=query.get('description', None),
										limit=query.get('limit', 20),
										offset=query.get('offset', 0),
										order=query.get('order', 'desc'),
										sort=query.get('sort', 'name'))

	return {
		'total': total,
		'groups': [utils.serializer(group) for group in groups]
	}


def layouts(request, layout_id=None):
	"""
	Handles any request (GET/POST) sent to /layouts or /layouts/<layout_id>.

	Parameters
	----------
	request - HTTP Request
	graph_id : string
		Unique ID of the graph.
	layout_id: string
		Unique ID of the layout.

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if request.method == "GET" and layout_id is None:
				return HttpResponse(json.dumps(get_layouts(request, query=request.GET)),
									content_type="application/json")
			elif request.method == "GET" and layout_id is not None:
				return HttpResponse(json.dumps(get_layout(request, layout_id)),
									content_type="application/json")
			elif request.method == "POST" and layout_id is None:
				return HttpResponse(json.dumps(add_layout(request, layout=json.loads(request.body))), content_type="application/json",
									status=201)
			elif request.method == "PUT" and layout_id is not None:
				return HttpResponse(json.dumps(update_layout(request, layout_id, layout=json.loads(request.body))),
									content_type="application/json",
									status=200)
			elif request.method == "DELETE" and layout_id is not None:
				delete_layout(request, layout_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted layout with id=%s" % (layout_id)
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def get_layouts(request, query=dict()):
	"""
	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the groups.
	graph_id : string
		Unique ID of the graph for the layout.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	name : string
		Search for groups with given name. In order to search for layouts with given name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all layouts with xyz in their name.
	order : string
		Defines the column sort order, can only be 'asc' or 'desc'.
	sort : string
		Defines which column will be sorted.

	Parameters
	----------
	query : dict
		Dictionary of query parameters.
	request : object
		HTTP GET Request.

	Returns
	-------
	total : integer
		Number of groups matching the request.
	groups : List of Layouts.
		List of Layout Objects with given limit and offset.

	Raises
	------

	Notes
	------
	"""

	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	total, layouts = graphs.search_layouts(request,
											owner_email=query.get('owner_email', None),
											name=query.get('name', None),
											graph_id=query.get('graph_id', None),
											limit=query.get('limit', 20),
											offset=query.get('offset', 0),
											order=query.get('order', 'desc'),
											sort=query.get('sort', 'name'))

	return {
		'total': total,
		'layouts': [utils.serializer(layout) for layout in layouts]
	}


def get_layout(request, layout_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	layout_id : string
		Unique ID of the layout.

	Returns
	-------
	layout: object

	Raises
	------

	Notes
	------

	"""
	return utils.serializer(graphs.get_layout_by_id(request, layout_id))


def add_layout(request, layout={}):
	"""
	Layout Parameters
	----------
	name : string
		Name of the layout. Required
	owner_email : string
		Email of the Owner of the graph. Required
	graph_id : string
		Unique ID of the graph for the layout. Required


	Parameters
	----------
	layout : dict
		Dictionary containing the data of the layout being added.
	request : object
		HTTP POST Request.

	Returns
	-------
	layout : object
		Newly created layout object.

	Raises
	------

	Notes
	------

	"""

	return utils.serializer(graphs.add_layout(request,
											 owner_email=layout.get('owner_email', None),
											 name=layout.get('name', None),
											 graph_id=layout.get('graph_id', None),
											 is_public=layout.get('is_public', None),
											 is_shared_with_groups=layout.get('is_shared_with_groups', None),
											 json=layout.get('json', None)))


def update_layout(request, layout_id, layout={}):
	"""
	Layout Parameters
	----------
	name : string
		Name of the layout. Required
	owner_email : string
		Email of the Owner of the graph. Required
	graph_id : string
		Unique ID of the graph for the layout. Required


	Parameters
	----------
	layout : dict
		Dictionary containing the data of the layout being added.
	layout_id : string
		Unique ID of the layout.
	request : object
		HTTP POST Request.

	Returns
	-------
	layout : object
		Updated layout object.

	Raises
	------

	Notes
	------


	"""

	return utils.serializer(graphs.update_layout(request, layout_id,
											 owner_email=layout.get('owner_email', None),
											 name=layout.get('name', None),
											 graph_id=layout.get('graph_id', None),
											 is_public=layout.get('is_public', None),
											 is_shared_with_groups=layout.get('is_shared_with_groups', None),
											 json=layout.get('json', None)))


def delete_layout(request, layout_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	layout_id : string
		Unique ID of the layout.

	Returns
	-------
	None

	Raises
	------

	Notes
	------

	"""
	graphs.delete_layout_by_id(request, layout_id)


def nodes(request, node_id=None):
	"""
	Handles any request (GET/POST) sent to nodes/ or nodes/<node_id>.

	Parameters
	----------
	request - HTTP Request
	node_id : string
		Unique ID of the node.

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if request.method == "GET" and node_id is None:
				return HttpResponse(json.dumps(get_nodes(request, query=request.GET)),
									content_type="application/json")
			elif request.method == "GET" and node_id is not None:
				return HttpResponse(json.dumps(get_node(request, node_id)),
									content_type="application/json")
			elif request.method == "POST" and node_id is None:
				return HttpResponse(json.dumps(add_node(request, node=json.loads(request.body))), content_type="application/json",
									status=201)
			elif request.method == "DELETE" and node_id is not None:
				delete_node(request, node_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted node with id=%s" % (node_id)
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def get_nodes(request, query={}):
	"""

	Query Parameters
	----------
	graph_id : string
		Unique ID of the graph.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	names : list of strings
		Search for groups with given names. In order to search for groups with given name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all groups with xyz in their name.
	labels : list of strings
		Search for groups with given labels. In order to search for groups with given label as a substring, wrap the label with percentage symbol. For example, %xyz% will search for all groups with xyz in their label.
	order : string
		Defines the column sort order, can only be 'asc' or 'desc'.
	sort : string
		Defines which column will be sorted.


	Parameters
	----------
	request : object
		HTTP GET Request.

	Returns
	-------
	total : integer
		Number of nodes matching the request.
	nodes : List of nodes.
		List of Node Objects with given limit and offset.

	Raises
	------

	Notes
	------

	"""
	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	total, nodes_list = graphs.search_nodes(request,
										graph_id=query.get('graph_id', None),
										names=query.getlist('names[]', None),
										labels=query.getlist('labels[]', None),
										limit=query.get('limit', 20),
										offset=query.get('offset', 0),
										order=query.get('order', 'desc'),
										sort=query.get('sort', 'name'))

	return {
		'total': total,
		'nodes': [utils.serializer(node) for node in nodes_list]
	}


def get_node(request, node_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	node_id : string
		Unique ID of the node.

	Returns
	-------
	node: object

	Raises
	------

	Notes
	------

	"""
	return utils.serializer(graphs.get_node_by_id(request, node_id))

def add_node(request, node={}):
	"""
	Node Parameters
	----------
	name : string
		Name of the node. Required
	label : string
		Label for the node. Optional
	graph_id : string
		Unique ID of the graph for the node. Required


	Parameters
	----------
	node : dict
		Dictionary containing the data of the node being added.
	request : object
		HTTP POST Request.

	Returns
	-------
	node : object
		Newly created node object.

	Raises
	------

	Notes
	------

	"""

	return utils.serializer(graphs.add_node(request,
											 name=node.get('name', None),
											 label=node.get('label', None),
											 graph_id=node.get('graph_id', None)))


def delete_node(request, node_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	node_id : string
		Unique ID of the node.

	Returns
	-------
	None

	Raises
	------

	Notes
	------

	"""
	graphs.delete_node_by_id(request, node_id)


def edges(request, edge_id=None):
	"""
	Handles any request (GET/POST) sent to edges/ or edges/<edge_id>.

	Parameters
	----------
	request - HTTP Request
	edge_id : string
		Unique ID of the edge.

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if request.method == "GET" and edge_id is None:
				return HttpResponse(json.dumps(get_edges(request, query=request.GET)),
									content_type="application/json")
			elif request.method == "GET" and edge_id is not None:
				return HttpResponse(json.dumps(get_edge(request, edge_id)),
									content_type="application/json")
			elif request.method == "POST" and edge_id is None:
				return HttpResponse(json.dumps(add_edge(request, edge=json.loads(request.body))), content_type="application/json",
									status=201)
			elif request.method == "DELETE" and edge_id is not None:
				delete_edge(request, edge_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted node with id=%s" % (edge_id)
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def get_edges(request, query={}):
	"""

	Query Parameters
	----------
	graph_id : string
		Unique ID of the graph.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	names : list of strings
		Search for edges with given names. In order to search for edges with given name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all edges with xyz in their name.
	edges : list of strings
		Search for edges with the edge between given given list of node names separated by colon. In order to search for edges with given edge as a substring, wrap the name of the nodes with percentage symbol. For example, %xyz%:%abc% will search for all edges with edge between nodes with 'xyz' and 'abc' in their node names.
	order : string
		Defines the column sort order, can only be 'asc' or 'desc'.
	sort : string
		Defines which column will be sorted.


	Parameters
	----------
	request : object
		HTTP GET Request.

	Returns
	-------
	total : integer
		Number of edges matching the request.
	edges : List of edges.
		List of Edge Objects with given limit and offset.

	Raises
	------

	Notes
	------

	"""
	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	total, edges_list = graphs.search_edges(request,
										graph_id=query.get('graph_id', None),
										names=query.getlist('names[]', None),
										edges=query.getlist('edges[]', None),
										limit=query.get('limit', 20),
										offset=query.get('offset', 0),
										order=query.get('order', 'desc'),
										sort=query.get('sort', 'name'))

	return {
		'total': total,
		'edges': [utils.serializer(edge) for edge in edges_list]
	}


def get_edge(request, edge_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	edge_id : string
		Unique ID of the edge.

	Returns
	-------
	edge: object

	Raises
	------

	Notes
	------

	"""
	return utils.serializer(graphs.get_edge_by_id(request, edge_id))

def add_edge(request, edge={}):
	"""
	Edge Parameters
	----------
	name : string
		Name of the edge. Required
	head_node_id : string
		Node ID for the head node. Required
	tail_node_id : string
		Node ID for the tail node. Required
	graph_id : string
		Unique ID of the graph for the edge. Required
	is_directed: Integer
		If the edge is directed or not. Default value is 0. Optional



	Parameters
	----------
	edge : dict
		Dictionary containing the data of the edge being added.
	request : object
		HTTP POST Request.

	Returns
	-------
	edge : object
		Newly created edge object.

	Raises
	------

	Notes
	------

	"""

	return utils.serializer(graphs.add_edge(request,
											 name=edge.get('name', None),
											 head_node_id=edge.get('head_node_id', None),
											 tail_node_id=edge.get('tail_node_id', None),
											 is_directed=edge.get('is_directed', 0),
											 graph_id=edge.get('graph_id', None)))


def delete_edge(request, edge_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	edge_id : string
		Unique ID of the edge.

	Returns
	-------
	None

	Raises
	------

	Notes
	------

	"""
	graphs.delete_edge_by_id(request, edge_id)

