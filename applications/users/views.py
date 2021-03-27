import json

import applications.users.controllers as users
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from graphspace import utils
import graphspace.authorization as authorization
from graphspace.wrappers import is_authenticated
from graphspace.exceptions import MethodNotAllowed, BadRequest, ErrorCodes, GraphSpaceError
from graphspace.utils import get_request_user


@is_authenticated(redirect_url='/')
def groups_page(request):
	"""
		Wrapper view for the groups page.

		:param request: HTTP GET Request.
	"""
	if 'GET' == request.method:
		context = RequestContext(request, {})
		return render(request, 'groups/index.html', context.flatten())
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


@is_authenticated(redirect_url='/')
def group_page(request, group_id):
	"""
		Wrapper view for the group page. /groups/<group_id>

		:param request: HTTP GET Request.

	Parameters
	----------
	group_id : string
		Unique ID of the group. Required
	"""
	if 'GET' == request.method:
		context = RequestContext(request, {})
		context.push({
			"group": _get_group(request, int(group_id)),
		})
		return render(request, 'group/index.html', context.flatten())
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


def join_group_page(request, group_id):
	"""
		Wrapper view for the join_group_page by invitation. /groups/<group_id>/invite/

		:param request: HTTP GET Request.

	Parameters
	----------
	group_id : string
		Unique ID of the group. Required
	"""
	context = RequestContext(request, {})

	if 'GET' == request.method:
		group = users.get_group_by_id(request, group_id)
		if group is not None and group.invite_code == request.GET.get('code', None):
			if request.session['uid'] is None:
				context.push({
					"group": group,
					"invite_code": request.GET.get('code', None)
				})
				return render(request, 'join_group/index.html', context.flatten())
			else:
				try:
					users.add_group_member(request, group_id, member_email=request.session['uid'])
				finally:
					return redirect('/groups/'+group_id)
		else:
			return redirect('/')  # TODO: change it to signup page. Currently we dont have a signup link.
	elif 'POST' == request.method:

		group = users.get_group_by_id(request, group_id)
		if group is not None and group.invite_code == request.POST.get('code', None):
			try:
				if request.session['uid'] is None:
					user = users.register(request, username=request.POST.get('user_id', None), password=request.POST.get('password', None))
					if user is not None:
						request.session['uid'] = user.email
						request.session['admin'] = user.is_admin

					users.add_group_member(request, group_id, member_id=user.id)

				return redirect('/groups/'+group_id)
			except GraphSpaceError as e:
				context.push({
					"error_message": e.get_message(),
					"group": group,
					"invite_code": request.POST.get('code', None)
				})
				return render(request, 'join_group/index.html', context.flatten())
		else:
			return redirect('/')  # TODO: change it to signup page. Currently we dont have a signup link.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


'''
Users APIs
'''


def users_ajax_api(request):
	"""
	Handles any request sent to following urls:
		/javascript/users

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _users_api(request)


def _users_api(request):
	"""
	Handles any request (GET/POST) sent to /users.

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if 'application/json' in request.META.get('HTTP_ACCEPT', None):
		if request.method == "GET":
			return HttpResponse(json.dumps(_get_users(request, query=request.GET)), content_type="application/json")
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_users(request, query={}):
	"""

	Query Parameters
	----------
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	email : string
		Search for users with given email. In order to search for users with given email as a substring, wrap the email with percentage symbol. For example, %xyz% will search for all users with xyz in their email.
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
	users : List of Users.
		List of User Objects with given limit and offset.

	Raises
	------

	Notes
	------

	"""

	# Validate search graph groups API request

	total, users_list = users.search_users(request,
										email=query.get('email', None),
										limit=query.get('limit', 20),
										offset=query.get('offset', 0),
										order=query.get('order', 'asc'),
										sort=query.get('sort', 'email'))

	return {
		'total': total,
		'users': [utils.serializer(user) for user in users_list]
	}

'''
Groups APIs
'''

@csrf_exempt
@is_authenticated()
def groups_rest_api(request, group_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/groups
		/api/v1/groups/<group_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _groups_api(request, group_id=group_id)


def groups_ajax_api(request, group_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/groups
		/javascript/groups/<group_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _groups_api(request, group_id=group_id)


def _groups_api(request, group_id=None):
	"""
	Handles any request (GET/POST) sent to /groups or groups/<group_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if request.method == "GET" and group_id is None:
			return HttpResponse(json.dumps(_get_groups(request, query=request.GET)), content_type="application/json")
		elif request.method == "GET" and group_id is not None:
			return HttpResponse(json.dumps(_get_group(request, group_id)), content_type="application/json",
								status=200)
		elif request.method == "POST" and group_id is None:
			return HttpResponse(json.dumps(_add_group(request, group=request.POST)), content_type="application/json",
								status=201)
		elif request.method == "PUT" and group_id is not None:
			return HttpResponse(json.dumps(_update_group(request, group_id, group=QueryDict(request.body))),
								content_type="application/json",
								status=200)
		elif request.method == "DELETE" and group_id is not None:
			_delete_group(request, group_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted group with id=%s" % group_id
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


@is_authenticated()
def _add_group(request, group={}):
	"""
	Group Parameters
	----------
	name : string
		Name of group. Required
	description : string
		Description of the group. Optional
	owner_email : string
		Email of the Owner of the groups. Required


	Parameters
	----------
	group : dict
		Dictionary containing the data of the group being added.
	request : object
		HTTP POST Request.

	Returns
	-------
	group : object
		Newly created group object.

	Raises
	------

	Notes
	------

	"""

	# Validate add graph API request
	user_role = authorization.user_role(request)
	if user_role == authorization.UserRole.LOGGED_IN:
		if get_request_user(request) != group.get('owner_email', None):
			raise BadRequest(request, error_code=ErrorCodes.Validation.CannotCreateGroupForOtherUser,
							 args=group.get('owner_email', None))

	return utils.serializer(users.add_group(request,
											name=request.POST.get('name', None),
											description=group.get('description', None),
											owner_email=group.get('owner_email', None)))


def _get_groups(request, query={}):
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

	# Validate search graph groups API request
	user_role = authorization.user_role(request)
	if user_role == authorization.UserRole.LOGGED_IN:
		if get_request_user(request) != query.get('member_email', None) \
				and get_request_user(request) != query.get('owner_email', None):
			raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedGroupAccess,
							 args=get_request_user(request))

	total, groups = users.search_groups(request,
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


def _get_group(request, group_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	group: object

	Raises
	------

	Notes
	------

	"""

	authorization.validate(request, permission='GROUP_READ', group_id=group_id)

	return utils.serializer(users.get_group_by_id(request, group_id))


@is_authenticated()
def _update_group(request, group_id, group={}):
	"""
	Group Parameters
	----------
	name : string
		Name of group. Required
	description : string
		Description of the group. Optional
	owner_email : string
		Email of the Owner of the groups. Required


	Parameters
	----------
	group : dict
		Dictionary containing the data of the group being added.
	request : object
		HTTP POST Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	group : object
		Newly created group object.

	Raises
	------

	Notes
	------

	"""
	authorization.validate(request, permission='GROUP_UPDATE', group_id=group_id)

	return utils.serializer(users.update_group(request, group_id=group_id,
											   name=group.get('name', None),
											   description=group.get('description', None),
											   owner_email=group.get('owner_email', None)))


@is_authenticated()
def _delete_group(request, group_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	None

	Raises
	------

	Notes
	------

	"""
	authorization.validate(request, permission='GROUP_DELETE', group_id=group_id)

	users.delete_group_by_id(request, group_id)


'''
Group Members APIs
'''

@csrf_exempt
@is_authenticated()
def group_members_rest_api(request, group_id, member_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/groups/<group_id>/members
		/api/v1/groups/<group_id>/members/<member_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _group_members_api(request, group_id, member_id=member_id)


def group_members_ajax_api(request, group_id, member_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/groups/<group_id>/members
		/javascript/groups/<group_id>/members/<member_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _group_members_api(request, group_id, member_id=member_id)


def _group_members_api(request, group_id, member_id=None):
	"""
	Handles any request (GET/POST) sent to groups/<group_id>/members or groups/<group_id>/members/<member_id>.

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if group_id is None:
			raise Exception("Group ID is required.")

		if request.method == "GET" and member_id is None:
			return HttpResponse(json.dumps(_get_group_members(request, group_id)),
								content_type="application/json")
		elif request.method == "POST" and member_id is None:
			return HttpResponse(json.dumps(_add_group_member(request, group_id)), content_type="application/json",
								status=201)
		elif request.method == "DELETE" and member_id is not None:
			_delete_group_member(request, group_id, member_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted member with id=%s from group with id=%s" % (member_id, group_id)
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_group_members(request, group_id):
	"""

	Parameters
	----------
	request : object
		HTTP GET Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	None

	Raises
	------

	Notes
	------

	"""
	authorization.validate(request, permission='GROUP_READ', group_id=group_id)

	members = users.get_group_members(request, group_id)
	return {
		"members": [utils.serializer(user) for user in members],
		"total": len(members)
	}


@is_authenticated()
def _add_group_member(request, group_id):
	"""
	Body Parameters
	----------
	member_id : string
		User ID of the member. Either of member_id or member_email is required.
	member_email : string
		Unique Email ID of the member. Either of member_id or member_email is required.

	Parameters
	----------
	request : object
		HTTP POST Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	group_to_user : object
		Newly added group_to_user relationship.

	Raises
	------

	Notes
	------
	"""
	authorization.validate(request, permission='GROUP_UPDATE', group_id=group_id)

	return utils.serializer(users.add_group_member(request,
												   group_id=group_id,
												   member_id=request.POST.get('member_id', None),
												   member_email=request.POST.get('member_email', None)))


@is_authenticated()
def _delete_group_member(request, group_id, member_id):
	"""
	Parameters
	----------
	request : object
		HTTP POST Request.
	group_id : string
		Unique ID of the group.
	member_id : string
		User ID of the member.


	Returns
	-------
	None

	Raises
	------

	Notes
	------
	"""
	authorization.validate(request, permission='GROUP_UPDATE', group_id=group_id)

	users.delete_group_member(request,
							  group_id=group_id,
							  member_id=member_id)


'''
Group Graphs APIs
'''

@csrf_exempt
@is_authenticated()
def group_graphs_rest_api(request, group_id, graph_id=None):
	"""
	Handles any request sent to following urls:
		/api/v1/groups/<group_id>/graphs
		/api/v1/groups/<group_id>/graphs/<graph_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _group_graphs_api(request, group_id, graph_id=graph_id)


def group_graphs_ajax_api(request, group_id, graph_id=None):
	"""
	Handles any request sent to following urls:
		/javascript/groups/<group_id>/graphs
		/javascript/groups/<group_id>/graphs/<graph_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _group_graphs_api(request, group_id, graph_id=graph_id)


def _group_graphs_api(request, group_id, graph_id=None):
	"""
	Handles any request (GET/POST) sent to groups/<group_id>/graphs or groups/<group_id>/graphs/<graph_id>.

	Parameters
	----------
	request - HTTP Request
	group_id : string
		Unique ID of the group.

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		if request.method == "GET" and graph_id is None:
			return HttpResponse(json.dumps(_get_group_graphs(request, group_id)),
								content_type="application/json")
		elif request.method == "POST" and graph_id is None:
			return HttpResponse(json.dumps(_add_group_graph(request, group_id)), content_type="application/json",
								status=201)
		elif request.method == "DELETE" and graph_id is not None:
			_delete_group_graph(request, group_id, graph_id)
			return HttpResponse(json.dumps({
				"message": "Successfully deleted graph with id=%s from group with id=%s" % (graph_id, group_id)
			}), content_type="application/json", status=200)
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_group_graphs(request, group_id):
	"""

	Query Parameters
	----------
	owner_email : string
		Email of the Owner of the graphs.
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	names : string
		Search for graphs with given names. In order to search for graphs with either of the given names as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all graphs with xyz in their name.
	nodes : list of strings
		Search for graphs with the given node names. In order to search for graphs with either of the given node names as a substring, wrap the node name with percentage symbol. For example, %xyz% will search for all graphs with xyz in their node names.
	edges : list of strings
		Search for graphs with the given edges. An edge can be represented as <head_node_name>:<tail_node_name>. In order to perform a substring on edges, wrap the node names with percentage symbol. For example, %xyz%:%abc% will search for all graphs with edges between nodes with xyz in their node names to nodes with abc in their node name.

	Parameters
	----------
	request : object
		HTTP GET Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	total : integer
		Number of groups matching the request.
	graphs : List of Graphs.
		List of Graphs Objects with given limit and offset.

	Raises
	------

	Notes
	------

	"""
	authorization.validate(request, permission='GROUP_READ', group_id=group_id)

	names = request.GET.get('names', None)
	nodes = request.GET.get('nodes', None)
	edges = request.GET.get('edges', None)
	total, graphs = users.search_group_graphs(request,
											  group_id=group_id,
											  owner_email=request.GET.get('owner_email', None),
											  names=names if names is None or isinstance(names, list) else [names],
											  nodes=nodes if nodes is None or isinstance(nodes, list) else [nodes],
											  edges=edges if edges is None or isinstance(edges, list) else [edges],
											  limit=request.GET.get('limit', 20),
											  offset=request.GET.get('offset', 0))

	return {
		'total': total,
		'graphs': [utils.serializer(graph) for graph in graphs]
	}


@is_authenticated()
def _add_group_graph(request, group_id):
	"""
	Body Parameters
	----------
	graph_id : string
		User ID of the member. Required

	Parameters
	----------
	request : object
		HTTP POST Request.
	group_id : string
		Unique ID of the group.

	Returns
	-------
	group_to_graph : object
		Newly added group_to_graph relationship.

	Raises
	------

	Notes
	------
	"""
	authorization.validate(request, permission='GRAPH_SHARE', graph_id=request.POST.get('graph_id', None))
	authorization.validate(request, permission='GROUP_SHARE', group_id=group_id)

	return utils.serializer(users.add_group_graph(request,
												  group_id=group_id,
												  graph_id=request.POST.get('graph_id', None)))


@is_authenticated()
def _delete_group_graph(request, group_id, graph_id):
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


