import json

import applications.users.controllers as users
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.template import RequestContext
from graphspace import utils


def groups_member(request):
	"""
		Render the Member Of page, showing the groups that the user belong to .

		:param request: HTTP GET Request

	"""
	return _groups_page(request, 'member')


def _groups_page(request, view_type):
	"""
		Wrapper view for the following pages:
			groups/
			groups/member/

		:param request: HTTP GET Request
		:param view_type: Type of view for the group (Example: owner of, member)
	"""
	context = RequestContext(request)  # context of the view to be passed in for rendering
	uid = request.session['uid'] if 'uid' in request.session else None  # Checks to see if a user is currently logged on
	context[
		'view_type'] = view_type  # Send view_type to front end to tell the user (through button color) where they are

	if uid is not None:  # User has to be logged in to get list of groups.
		context['page'] = request.GET.get('page', 0)
		context['page_size'] = request.GET.get('pageSize', 10)
		context['order_by'] = 'group_ascending' if len(request.GET.get('order', '').strip()) == 0 else request.GET.get(
			'order').strip()

		context['member_groups'] = users.get_groups_by_member_id(request, uid, context['page'], context[
			'page_size'])  # Get all the groups where logged in user is a member.
		context['owned_groups'] = users.get_groups_by_owner_id(request, uid, context['page'], context[
			'page_size'])  # Get all the groups owned by the logged in user.

		return render(request, 'graphs/groups.html', context)
	else:
		context[
			'Error'] = "You need to be logged in and also be a member of this group in order to see this group's contents!"
		return render(request, 'graphs/error.html', context)

	# if view_type == 'owner of' and context['my_groups'] == 0:
	# 	context['message'] = "It appears that you are not an owner of any group.  Please create a group in order to own a group."
	# elif view_type == 'member' and context['member_groups'] == 0 :
	# 	context['message'] = "It appears as if you are not a member of any group. Please join a group in order for them to appear here."
	# else:
	# 	context['message'] = "It appears as if there are currently no groups on GraphSpace."


def add_group(request, group={}):
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
	return utils.serializer(users.add_group(request,
											name=request.POST.get('name', None),
											description=group.get('description', None),
											owner_email=group.get('owner_email', None)))


def get_groups(request, query={}):
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


def get_group(request, group_id):
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
	return utils.serializer(users.get_group_by_id(request, group_id))


def update_group(request, group_id, group={}):
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
	return utils.serializer(users.update_group(request, group_id=group_id,
											   name=group.get('name', None),
											   description=group.get('description', None),
											   owner_email=group.get('owner_email', None)))


def delete_group(request, group_id):
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
	users.delete_group_by_id(request, group_id)


def groups(request, group_id=None):
	"""
	Handles any request (GET/POST) sent to /groups or groups/<group_id>

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if request.method == "GET" and group_id is None:
				return HttpResponse(json.dumps(get_groups(request, query=request.GET)), content_type="application/json")
			elif request.method == "GET" and group_id is not None:
				return HttpResponse(json.dumps(get_group(request, group_id)), content_type="application/json",
									status=200)
			elif request.method == "POST" and group_id is None:
				return HttpResponse(json.dumps(add_group(request, group=request.POST)), content_type="application/json", status=201)
			elif request.method == "PUT" and group_id is not None:
				return HttpResponse(json.dumps(update_group(request, group_id, group=QueryDict(request.body))), content_type="application/json",
									status=200)
			elif request.method == "DELETE" and group_id is not None:
				delete_group(request, group_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted group with id=%s" % group_id
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def get_group_members(request, group_id):
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
	members = users.get_group_members(request, group_id)
	return {
		"members": [utils.serializer(user) for user in members],
		"total": len(members)
	}


def add_group_member(request, group_id):
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
	return utils.serializer(users.add_group_member(request,
												   group_id=group_id,
												   member_id=request.POST.get('member_id', None),
												   member_email=request.POST.get('member_email', None)))


def delete_group_member(request, group_id, member_id):
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
	users.delete_group_member(request,
							  group_id=group_id,
							  member_id=member_id)


def group_members(request, group_id, member_id=None):
	"""
	Handles any request (GET/POST) sent to groups/<group_id>/members or groups/<group_id>/members/<member_id>.

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if request.META.get('HTTP_ACCEPT', None) == 'application/json':
		try:
			if group_id is None:
				raise Exception("Group ID is required.")

			if request.method == "GET" and member_id is None:
				return HttpResponse(json.dumps(get_group_members(request, group_id)),
									content_type="application/json")
			elif request.method == "POST" and member_id is None:
				return HttpResponse(json.dumps(add_group_member(request, group_id)), content_type="application/json",
									status=201)
			elif request.method == "DELETE" and member_id is not None:
				delete_group_member(request, group_id, member_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted member with id=%s from group with id=%s" % (member_id, group_id)
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def group_graphs(request, group_id, graph_id=None):
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
		try:
			if group_id is None:
				raise Exception("Group ID is required.")

			if request.method == "GET" and graph_id is None:
				return HttpResponse(json.dumps(get_group_graphs(request, group_id)),
									content_type="application/json")
			elif request.method == "POST" and graph_id is None:
				return HttpResponse(json.dumps(add_group_graph(request, group_id)), content_type="application/json",
									status=201)
			elif request.method == "DELETE" and graph_id is not None:
				delete_group_graph(request, group_id, graph_id)
				return HttpResponse(json.dumps({
					"message": "Successfully deleted graph with id=%s from group with id=%s" % (graph_id, group_id)
				}), content_type="application/json", status=200)
		except Exception as e:
			return HttpResponse(json.dumps({
				"message": "BAD REQUEST"
			}), content_type="application/json", status=400)


def get_group_graphs(request, group_id):
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


def add_group_graph(request, group_id):
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
	return utils.serializer(users.add_group_graph(request,
												  group_id=group_id,
												  graph_id=request.POST.get('graph_id', None)))


def delete_group_graph(request, group_id, graph_id):
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


def groups_page(request):
	"""
		Wrapper view for the groups page.

		:param request: HTTP GET Request.
	"""
	context = RequestContext(request, {})
	uid = request.session['uid'] if 'uid' in request.session else None
	if uid is not None:
		context.push({
			"owner_of": get_groups(request, query={'owner_email': uid}),
			"member_of": get_groups(request, query={'member_email': uid}),
		})
		if request.META.get('HTTP_ACCEPT', None) == 'application/json':
			return HttpResponse(json.dumps(context.dicts),content_type="application/json")
		else:
			return render(request, 'graphs/groups.html', context)
	else:
		context['Error'] = "You need to be logged in and also be a member of this group in order to see this group's contents!"
		return render(request, 'graphs/error.html', context)


def group_page(request, group_id):
	"""
		Wrapper view for the group page. /groups/<group_id>

		:param request: HTTP GET Request.

	Parameters
	----------
	group_id : string
		Unique ID of the group. Required
	"""
	context = RequestContext(request, {})
	uid = request.session['uid'] if 'uid' in request.session else None
	if uid is not None:
		context.push({
			"group": get_group(request, group_id),
		})
		if request.META.get('HTTP_ACCEPT', None) == 'application/json':
			return HttpResponse(json.dumps(context.dicts),content_type="application/json")
		else:
			return render(request, 'graphs/group.html', context)
	else:
		context['Error'] = "You need to be logged in and also be a member of this group in order to see this group's contents!"
		return render(request, 'graphs/error.html', context)
