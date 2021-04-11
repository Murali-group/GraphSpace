import json

import applications.graphs.controllers as graphs
import applications.users.controllers as users
import graphspace.authorization as authorization
import graphspace.utils as utils
from django.conf import settings
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from graphspace.exceptions import MethodNotAllowed, BadRequest, ErrorCodes
from graphspace.utils import get_request_user
from graphspace.wrappers import is_authenticated


def upload_graph_page(request):
	context = RequestContext(request, {})

	if request.method == 'POST':
		try:
			graph = _add_graph(request, graph={
				'name': request.POST.get('name', None),
				'owner_email': request.POST.get('owner_email', None),
				'is_public': request.POST.get('is_public', None),
				'graph_json': json.loads(request.FILES['graph_file'].read()),
				'style_json': json.loads(request.FILES['style_file'].read()) if 'style_file' in request.FILES else None
			})
			context['Success'] = settings.URL_PATH + "graphs/" + str(graph['id'])
		except Exception as e:
			context['Error'] = str(e)

		return render(request, 'upload_graph/index.html', context.flatten())
	else:
		return render(request, 'upload_graph/index.html', context.flatten())


def graphs_page(request):
	"""
		Wrapper view function for the following pages:
		/graphs/

		Parameters
		----------
		request : HTTP Request

		Returns
		-------
		response : HTML Page Response
			Rendered graphs list page in HTML.

		Raises
		------
		MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

		Notes
		------
	"""
	if 'GET' == request.method:
		context = RequestContext(request, {
			"tags": request.GET.get('tags', '')
		})
		return render(request, 'graphs/index.html', context.flatten())
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


def graph_page_by_name(request, email, graph_name):
	"""
	Redirects to the appropriate graph page. This is only for supporting older URLs.

	Parameters
	----------
	email : string
		User Email Address. Required
	graph_name : string
		Name of the Graph.
	"""
	graph = graphs.get_graph_by_name(request, owner_email=email, name=graph_name)
	if graph is not None:
		return redirect('/graphs/' + str(graph.id))
	else:
		return redirect('/')


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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	uid = request.session['uid'] if 'uid' in request.session else None

	context.push({"graph": _get_graph(request, graph_id)})
	context.push({"is_posted_by_public_user": 'public_user' in context["graph"]["owner_email"]})
	context.push({"default_layout_id": str(context["graph"]['default_layout_id']) if context["graph"][
		'default_layout_id'] else None})

	default_layout = graphs.get_layout_by_id(request, context["graph"]['default_layout_id']) if context["graph"][
		                                                                                            'default_layout_id'] is not None else None

	if default_layout is not None and (default_layout.is_shared == 1 or default_layout.owner_email == uid) and request.GET.get(
			'user_layout') is None and request.GET.get('auto_layout') is None:
		if '?' in request.get_full_path():
			return redirect(request.get_full_path() + '&user_layout=' + context["default_layout_id"])
		else:
			return redirect(request.get_full_path() + '?user_layout=' + context["default_layout_id"])

	context['graph_json_string'] = json.dumps(context['graph']['graph_json'])
	context['data'] = {k: json.dumps(v, encoding='ascii') for k,v in context['graph']['graph_json']['data'].items()}
	context['style_json_string'] = json.dumps(context['graph']['style_json'])
	context['description'] = context['graph']['graph_json']['data']['description'] if 'data' in context[
		'graph']['graph_json'] and 'description' in context['graph']['graph_json']['data'] else ''

	if 'data' in context['graph']['graph_json'] and 'title' in context['graph']['graph_json']['data']:
		context['title'] = context['graph']['graph_json']['data']['title']
	elif 'data' in context['graph']['graph_json'] and 'name' in context['graph']['graph_json']['data']:
		context['title'] = context['graph']['graph_json']['data']['name']
	else:
		context['title'] = ''

	if uid is not None:
		context.push({
			"groups": [utils.serializer(group) for group in
			           users.get_groups_by_member_id(request, member_id=users.get_user(request, uid).id)],
			"shared_groups":
				_get_graph_groups(request, graph_id, query={'limit': None, 'offset': None, 'member_email': uid})[
					'groups']
		})

		shared_group_ids = [group['id'] for group in context["shared_groups"]]
		for group in context['groups']:
			group['is_shared'] = 1 if group['id'] in shared_group_ids else 0

	return render(request, 'graph/index.html', context.flatten())


'''
Graphs APIs
'''


@csrf_exempt
@is_authenticated()
def graphs_rest_api(request, graph_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/graphs
		/api/v1/graphs/<graph_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graphs_api(request, graph_id=graph_id)


def graphs_ajax_api(request, graph_id=None):
	"""
	Handles any request sent to following urls:
		/ajax/graphs
		/ajax/graphs/<graph_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graphs_api(request, graph_id=graph_id)


@csrf_exempt
def graphs_advanced_search_ajax_api(request):
	"""
	Handles any request sent to following urls:
		/ajax/graphs

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if request.method == "POST":
			querydict = QueryDict('', mutable=True)
			querydict.update(request.GET)
			queryparams = querydict

			# Validate search graphs API request
			user_role = authorization.user_role(request)
			if user_role == authorization.UserRole.LOGGED_IN:
				if queryparams.get('owner_email', None) is None \
						and queryparams.get('member_email', None) is None \
						and queryparams.get('is_public', None) != '1':
					raise BadRequest(request, error_code=ErrorCodes.Validation.IsPublicNotSet)
				if queryparams.get('is_public', None) != '1':
					if get_request_user(request) != queryparams.get('member_email', None) \
							and get_request_user(request) != queryparams.get('owner_email', None):
						raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedGraphAccess,
						                 args=queryparams.get('owner_email', None))

			# graphs_list is already a json string dump of the graph objects. JSONification is done
			# in controllers.py
			total, graphs_list = graphs.search_graphs1(request,
			                                           owner_email=queryparams.get('owner_email', None),
			                                           member_email=queryparams.get('member_email', None),
			                                           names=list(filter(None, queryparams.getlist('names[]', []))),
			                                           is_public=queryparams.get('is_public', None),
			                                           nodes=list(filter(None, queryparams.getlist('nodes[]', []))),
			                                           edges=list(filter(None, queryparams.getlist('edges[]', []))),
			                                           tags=list(filter(None, queryparams.getlist('tags[]', []))),
			                                           limit=queryparams.get('limit', 20),
			                                           offset=queryparams.get('offset', 0),
			                                           order=queryparams.get('order', 'desc'),
			                                           sort=queryparams.get('sort', 'name'),
			                                           query=json.loads(request.body))

			return HttpResponse(json.dumps({
				'total': total,
				'graphs': graphs_list
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like GET, OPTIONS etc.
	else:
		raise BadRequest(request)


def _graphs_api(request, graph_id=None):
	"""
	Handles any request sent to following urls:
		/graphs
		/graphs/<graph_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET, POST, PUT or UPDATE.
	BadRequest: If HTTP_ACCEPT header is not set to application/json.

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if request.method == "GET" and graph_id is None:
			return HttpResponse(json.dumps(_get_graphs(request, query=request.GET)), content_type="application/json")
		elif request.method == "GET" and graph_id is not None:
			return HttpResponse(json.dumps(_get_graph(request, graph_id)), content_type="application/json",
			                    status=200)
		elif request.method == "POST" and graph_id is None:
			return HttpResponse(json.dumps(_add_graph(request, graph=json.loads(request.body))),
			                    content_type="application/json", status=201)
		elif request.method == "PUT" and graph_id is not None:
			return HttpResponse(json.dumps(_update_graph(request, graph_id, graph=json.loads(request.body))),
			                    content_type="application/json",
			                    status=200)
		elif request.method == "DELETE" and graph_id is not None:
			_delete_graph(request, graph_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted graph with id=%s" % graph_id
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_graphs(request, query=dict()):
	"""
	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the graphs. Required if member_email is not provided, user is not admin and is_public is not set to True.
	member_email : string
		Email of the User with which the graphs are shared. Required if owner_email is not provided, user is not admin and is_public is not set to True.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	is_public: integer
		Search for graphs with given visibility. In order to search for public graphs set is_public to 1. Required if member_email & owner_email are not provided.
		In order to search for private graphs set is_public to 0. In order to search for all graphs set is_public to None.
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
	BadRequest - `is_public` is required to be set to True when `owner_email` and `member_email` are not provided.

	BadRequest - `User is not authorized to access private graphs created by given owner. This means either the graph belongs to a different owner
	or graph is not shared with the user.

	Notes
	------
	"""

	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	# Validate search graphs API request
	user_role = authorization.user_role(request)
	if user_role == authorization.UserRole.LOGGED_IN:
		if query.get('owner_email', None) is None \
				and query.get('member_email', None) is None \
				and query.get('is_public', None) != '1':
			raise BadRequest(request, error_code=ErrorCodes.Validation.IsPublicNotSet)
		if query.get('is_public', None) != '1':
			if get_request_user(request) != query.get('member_email', None) \
					and get_request_user(request) != query.get('owner_email', None):
				raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedGraphAccess,
				                 args=query.get('owner_email', None))

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
		'graphs': [utils.serializer(graph, summary=True) for graph in graphs_list]
	}


def _get_graph(request, graph_id):
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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	return utils.serializer(graphs.get_graph_by_id(request, graph_id))


def _add_graph(request, graph={}):
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
	BadRequest - Cannot create graph for user other than the requesting user.

	Notes
	------

	"""

	# Validate add graph API request
	user_role = authorization.user_role(request)
	graph_name = graph.get('name')
	if len(graph_name)>256: # To check if the Graph Name is within the given range(i.e maximum 256 characters long)
		raise BadRequest(request, error_code=ErrorCodes.Validation.GraphNameSize)
	if user_role == authorization.UserRole.LOGGED_IN:
		if get_request_user(request) != graph.get('owner_email', None):
			raise BadRequest(request, error_code=ErrorCodes.Validation.CannotCreateGraphForOtherUser,
			                 args=graph.get('owner_email', None))
	elif user_role == authorization.UserRole.LOGGED_OFF and graph.get('owner_email', None) is not None:
		raise BadRequest(request, error_code=ErrorCodes.Validation.CannotCreateGraphForOtherUser,
		                 args=graph.get('owner_email', None))

	return utils.serializer(graphs.add_graph(request,
	                                         name=graph.get('name', None),
	                                         is_public=graph.get('is_public', None),
	                                         graph_json=graph.get('graph_json', None),
	                                         style_json=graph.get('style_json', None),
	                                         tags=graph.get('tags', None),
	                                         owner_email=graph.get('owner_email', None)))


@is_authenticated()
def _update_graph(request, graph_id, graph={}):
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

	It will update the owner_email only if user has admin access otherwise user cannot update the owner email.

	"""
	authorization.validate(request, permission='GRAPH_UPDATE', graph_id=graph_id)
	user_role = authorization.user_role(request)

	if 'update_legend_format' in graph:
	        return utils.serializer(graphs.update_graph_with_html_legend(request, graph_id=graph_id, param=graph))

	return utils.serializer(graphs.update_graph(request,
	                                            graph_id=graph_id,
	                                            name=graph.get('name', None),
	                                            is_public=graph.get('is_public', None),
	                                            graph_json=graph.get('graph_json', None),
	                                            style_json=graph.get('style_json', None),
	                                            owner_email=graph.get('owner_email',
	                                                                  None) if user_role == authorization.UserRole.ADMIN else None,
	                                            default_layout_id=graph.get('default_layout_id', None)))


@is_authenticated()
def _delete_graph(request, graph_id):
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
	authorization.validate(request, permission='GRAPH_DELETE', graph_id=graph_id)
	graphs.delete_graph_by_id(request, graph_id)


'''
Graph Groups APIs.
'''


@csrf_exempt
@is_authenticated()
def graph_groups_rest_api(request, graph_id, group_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/graphs/<graph_id>/groups
		/api/v1/graphs/<graph_id>/groups/<group_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_groups_api(request, graph_id, group_id=group_id)


def graph_groups_ajax_api(request, graph_id, group_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/graphs/<graph_id>/groups
		/javascript/graphs/<graph_id>/groups/<group_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_groups_api(request, graph_id, group_id=group_id)


@is_authenticated()
def _graph_groups_api(request, graph_id, group_id=None):
	"""
	Handles any request (GET/POST) sent to graphs/<graph_id>/groups or graphs/<graph_id>/groups/<group_id>.

	Parameters
	----------
	request - HTTP Request
	graph_id : string
		Unique ID of the graph.

	Returns
	-------

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET, POST, PUT or UPDATE.
	BadRequest: If HTTP_ACCEPT header is not set to application/json.
	BadRequest: If graph_id is missing.

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if graph_id is None:
			raise BadRequest(request, error_code=ErrorCodes.Validation.GraphIDMissing)

		if request.method == "GET" and group_id is None:
			return HttpResponse(json.dumps(_get_graph_groups(request, graph_id, query=request.GET)),
			                    content_type="application/json")
		elif request.method == "POST" and group_id is None:
			return HttpResponse(json.dumps(_add_graph_group(request, graph_id, group=json.loads(request.body))),
			                    content_type="application/json",
			                    status=201)
		elif request.method == "DELETE" and group_id is not None:
			_delete_graph_group(request, graph_id, group_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted graph with id=%s from group with id=%s" % (graph_id, group_id)
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _add_graph_group(request, graph_id, group={}):
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
	authorization.validate(request, permission='GRAPH_SHARE', graph_id=graph_id)
	authorization.validate(request, permission='GROUP_SHARE', group_id=group.get('group_id', None))

	return utils.serializer(users.add_group_graph(request,
	                                              graph_id=graph_id,
	                                              group_id=group.get('group_id', None)))


def _delete_graph_group(request, graph_id, group_id):
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
	authorization.validate(request, permission='GRAPH_SHARE', graph_id=graph_id)
	authorization.validate(request, permission='GROUP_SHARE', group_id=group_id)

	users.delete_group_graph(request,
	                         group_id=group_id,
	                         graph_id=graph_id)


def _get_graph_groups(request, graph_id, query={}):
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
	BadRequest: If the user is not admin and tries to access groups where user is neither owner or member.

	Notes
	------

	"""
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	# Validate search graph groups API request
	user_role = authorization.user_role(request)
	if user_role == authorization.UserRole.LOGGED_IN:
		if query.get('is_public', None) is not True:
			if get_request_user(request) != query.get('member_email', None) \
					and get_request_user(request) != query.get('owner_email', None):
				raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedGroupAccess,
				                 args=get_request_user(request))

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


'''
Graph Layouts APIs
'''


@csrf_exempt
@is_authenticated()
def graph_layouts_rest_api(request, graph_id, layout_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/graphs/<graph_id>/layouts
		/api/v1/graphs/<graph_id>/layouts/<layout_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_layouts_api(request, graph_id, layout_id=layout_id)


def graph_layouts_ajax_api(request, graph_id, layout_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/graphs/<graph_id>/layouts
		/javascript/graphs/<graph_id>/layouts/<layout_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_layouts_api(request, graph_id, layout_id=layout_id)


def _graph_layouts_api(request, graph_id, layout_id=None):
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
		if request.method == "GET" and layout_id is None:
			return HttpResponse(json.dumps(_get_layouts(request, graph_id, query=request.GET)),
			                    content_type="application/json")
		elif request.method == "GET" and layout_id is not None:
			return HttpResponse(json.dumps(_get_layout(request, graph_id, layout_id)),
			                    content_type="application/json")
		elif request.method == "POST" and layout_id is None:
			return HttpResponse(json.dumps(_add_layout(request, graph_id, layout=json.loads(request.body))),
			                    content_type="application/json",
			                    status=201)
		elif request.method == "PUT" and layout_id is not None:
			return HttpResponse(
				json.dumps(_update_layout(request, graph_id, layout_id, layout=json.loads(request.body))),
				content_type="application/json",
				status=200)
		elif request.method == "DELETE" and layout_id is not None:
			_delete_layout(request, graph_id, layout_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted layout with id=%s" % (layout_id)
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_layouts(request, graph_id, query=dict()):
	"""
	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the groups.
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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	# Validate search layouts API request
	user_role = authorization.user_role(request)
	if user_role == authorization.UserRole.LOGGED_IN:
		if get_request_user(request) != query.get('owner_email', None) \
				and (query.get('is_shared', None) is None or int(query.get('is_shared', 0)) != 1):
			raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedLayoutAccess, args=get_request_user(request))

	total, layouts = graphs.search_layouts(request,
	                                       owner_email=query.get('owner_email', None),
	                                       name=query.get('name', None),
	                                       is_shared=query.get('is_shared', None),
	                                       graph_id=graph_id,
	                                       limit=query.get('limit', 20),
	                                       offset=query.get('offset', 0),
	                                       order=query.get('order', 'desc'),
	                                       sort=query.get('sort', 'name'))

	return {
		'total': total,
		'layouts': [utils.serializer(layout) for layout in layouts]
	}


def _get_layout(request, graph_id, layout_id):
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
	authorization.validate(request, permission='LAYOUT_READ', layout_id=layout_id)

	return utils.serializer(graphs.get_layout_by_id(request, layout_id))


@is_authenticated()
def _add_layout(request, graph_id, layout={}):
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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	# Validate add graph API request
	user_role = authorization.user_role(request)
	if user_role == authorization.UserRole.LOGGED_IN:
		if get_request_user(request) != layout.get('owner_email', None):
			raise BadRequest(request, error_code=ErrorCodes.Validation.CannotCreateLayoutForOtherUser,
			                 args=layout.get('owner_email', None))

	return utils.serializer(graphs.add_layout(request,
	                                          owner_email=layout.get('owner_email', None),
	                                          name=layout.get('name', None),
	                                          graph_id=layout.get('graph_id', None),
	                                          is_shared=layout.get('is_shared', None),
	                                          positions_json=layout.get('positions_json', None),
	                                          style_json=layout.get('style_json', None),
	                                          ))


@is_authenticated()
def _update_layout(request, graph_id, layout_id, layout={}):
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
	It will update the owner_email only if user has admin access otherwise user cannot update the owner email.

	"""
	authorization.validate(request, permission='LAYOUT_UPDATE', layout_id=layout_id)
	user_role = authorization.user_role(request)

	return utils.serializer(graphs.update_layout(request, layout_id,
	                                             owner_email=layout.get('owner_email',
	                                                                    None) if user_role == authorization.UserRole.ADMIN else None,
	                                             name=layout.get('name', None),
	                                             graph_id=layout.get('graph_id', None),
	                                             is_shared=layout.get('is_shared', None),
	                                             positions_json=layout.get('positions_json', None),
	                                             style_json=layout.get('style_json', None),
	                                             ))


@is_authenticated()
def _delete_layout(request, graph_id, layout_id):
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
	authorization.validate(request, permission='LAYOUT_DELETE', layout_id=layout_id)

	graphs.delete_layout_by_id(request, layout_id)


@csrf_exempt
@is_authenticated()
def graph_nodes_rest_api(request, graph_id, node_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/graphs/<graph_id>/nodes
		/api/v1/graphs/<graph_id>/nodes/<node_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_nodes_api(request, graph_id, node_id=node_id)


def graph_nodes_ajax_api(request, graph_id, node_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/graphs/<graph_id>/nodes
		/javascript/graphs/<graph_id>/nodes/<node_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_nodes_api(request, graph_id, node_id=node_id)


def _graph_nodes_api(request, graph_id, node_id=None):
	"""
	Handles any request (GET/POST) sent to nodes/ or nodes/<node_id>.

	Parameters
	----------
	request - HTTP Request
	graph_id : string
		Unique ID of the graph.
	node_id : string
		Unique ID of the node.

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if request.method == "GET" and node_id is None:
			return HttpResponse(json.dumps(_get_nodes(request, graph_id, query=request.GET)),
			                    content_type="application/json")
		elif request.method == "GET" and node_id is not None:
			return HttpResponse(json.dumps(_get_node(request, graph_id, node_id)),
			                    content_type="application/json")
		elif request.method == "POST" and node_id is None:
			return HttpResponse(json.dumps(_add_node(request, graph_id, node=json.loads(request.body))),
			                    content_type="application/json",
			                    status=201)
		elif request.method == "DELETE" and node_id is not None:
			_delete_node(request, graph_id, node_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted node with id=%s" % (node_id)
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_nodes(request, graph_id, query={}):
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

	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	total, nodes_list = graphs.search_nodes(request,
	                                        graph_id=graph_id,
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


def _get_node(request, graph_id, node_id):
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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)
	return utils.serializer(graphs.get_node_by_id(request, node_id))


@is_authenticated()
def _add_node(request, graph_id, node={}):
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
	authorization.validate(request, permission='GRAPH_UPDATE', graph_id=graph_id)

	return utils.serializer(graphs.add_node(request,
	                                        name=node.get('name', None),
	                                        label=node.get('label', None),
	                                        graph_id=graph_id))


@is_authenticated()
def _delete_node(request, graph_id, node_id):
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
	authorization.validate(request, permission='GRAPH_UPDATE', graph_id=graph_id)

	graphs.delete_node_by_id(request, node_id)


@csrf_exempt
@is_authenticated()
def graph_edges_rest_api(request, graph_id, edge_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/graphs/<graph_id>/edges
		/api/v1/graphs/<graph_id>/edges/<edge_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_edges_api(request, graph_id, edge_id=edge_id)


def graph_edges_ajax_api(request, graph_id, edge_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/graphs/<graph_id>/edges
		/javascript/graphs/<graph_id>/edges/<edge_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _graph_edges_api(request, graph_id, edge_id=edge_id)


def _graph_edges_api(request, graph_id, edge_id=None):
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
		if request.method == "GET" and edge_id is None:
			return HttpResponse(json.dumps(_get_edges(request, graph_id, query=request.GET)),
			                    content_type="application/json")
		elif request.method == "GET" and edge_id is not None:
			return HttpResponse(json.dumps(_get_edge(request, graph_id, edge_id)),
			                    content_type="application/json")
		elif request.method == "POST" and edge_id is None:
			return HttpResponse(json.dumps(_add_edge(request, graph_id, edge=json.loads(request.body))),
			                    content_type="application/json",
			                    status=201)
		elif request.method == "DELETE" and edge_id is not None:
			_delete_edge(request, graph_id, edge_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted node with id=%s" % (edge_id)
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_edges(request, graph_id, query={}):
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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	querydict = QueryDict('', mutable=True)
	querydict.update(query)
	query = querydict

	total, edges_list = graphs.search_edges(request,
	                                        graph_id=graph_id,
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


def _get_edge(request, graph_id, edge_id):
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
	authorization.validate(request, permission='GRAPH_READ', graph_id=graph_id)

	return utils.serializer(graphs.get_edge_by_id(request, edge_id))


@is_authenticated()
def _add_edge(request, graph_id, edge={}):
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
	authorization.validate(request, permission='GRAPH_UPDATE', graph_id=graph_id)

	return utils.serializer(graphs.add_edge(request,
	                                        name=edge.get('name', None),
	                                        head_node_id=edge.get('head_node_id', None),
	                                        tail_node_id=edge.get('tail_node_id', None),
	                                        is_directed=edge.get('is_directed', 0),
	                                        graph_id=graph_id))


@is_authenticated()
def _delete_edge(request, graph_id, edge_id):
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
	authorization.validate(request, permission='GRAPH_UPDATE', graph_id=graph_id)

	graphs.delete_edge_by_id(request, edge_id)
