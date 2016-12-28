import applications.users as users
import applications.graphs as graphs


def validate(request, permission, graph_id=None, group_id=None):
	if graph_id is not None:
		if permission == 'GRAPH_READ' and not graphs.controllers.is_user_authorized_to_view_graph(request, username=request.session['uid'], graph_id = graph_id):
			raise Exception('Unauthorized')
		if permission == 'GRAPH_UPDATE' and not graphs.controllers.is_user_authorized_to_update_graph(request, username=request.session['uid'], graph_id = graph_id):
			raise Exception('Unauthorized')
		if permission == 'GRAPH_DELETE' and not graphs.controllers.is_user_authorized_to_delete_graph(request, username=request.session['uid'], graph_id = graph_id):
			raise Exception('Unauthorized')
		if permission == 'GRAPH_SHARE' and not graphs.controllers.is_user_authorized_to_share_graph(request, username=request.session['uid'], graph_id = graph_id):
			raise Exception('Unauthorized')
	if group_id is not None:
		if permission == 'GROUP_READ' and not users.controllers.is_user_authorized_to_view_group(request, username=request.session['uid'], group_id = group_arg):
			raise Exception('Unauthorized')
		if permission == 'GROUP_UPDATE' and not users.controllers.is_user_authorized_to_update_group(request, username=request.session['uid'], group_id = group_arg):
			raise Exception('Unauthorized')
		if permission == 'GROUP_DELETE' and not users.controllers.is_user_authorized_to_delete_group(request, username=request.session['uid'], group_id = group_arg):
			raise Exception('Unauthorized')
		if permission == 'GROUP_SHARE' and not users.controllers.is_user_authorized_to_share_with_group(request, username=request.session['uid'], group_id = group_arg):
			raise Exception('Unauthorized')
