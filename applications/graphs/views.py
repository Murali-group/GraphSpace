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


def get_graphs(request, query=dict()):
	"""
	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the graphs.
	member_email: string
		Email of the member of the groups the graphs are shared with.
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
			"shared_groups": get_graph_groups(request, graph_id, query={'limit': None,'offset': None})['groups']
		})
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
				return HttpResponse(json.dumps(add_graph_group(request, graph_id)), content_type="application/json",
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


def add_graph_group(request, graph_id):
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
												  group_id=request.POST.get('group_id', None)))


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
