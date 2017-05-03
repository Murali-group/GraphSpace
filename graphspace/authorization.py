import applications.users as users
import applications.graphs as graphs
from graphspace.exceptions import UserNotAuthorized
from graphspace.utils import get_request_user


class UserRole:
	ADMIN = 3
	LOGGED_IN = 2
	LOGGED_OFF = 1 # When user is not logged in to GraphSpace.


def user_role(request):
	"""
	Returns the user role for the user making the request.

	Parameters
	----------
	request: HTTP request

	Returns
	-------
	Returns UserRole
	"""
	user_email = get_request_user(request)
	user = users.controllers.get_user(request, user_email) if user_email is not None else None
	if user is None:
		return UserRole.LOGGED_OFF
	elif user.is_admin:
		return UserRole.ADMIN
	else:
		return UserRole.LOGGED_IN


def validate(request, permission, graph_id=None, group_id=None, layout_id=None):
	"""
	Validates if the user has the given permissions based on information like graph id, group id or layout id.

	Returns
	-------
	Nothing

	Raises
	-------
	UserNotAuthorized - if user doesnt have the given permission.

	"""

	# TODO: Each application module should implement a validate method.
	# Then this validate method can plug into the implemented validate method to expose overall validation functionality for the project.

	if graph_id is not None:
		if permission == 'GRAPH_READ' and not graphs.controllers.is_user_authorized_to_view_graph(request, username=get_request_user(request), graph_id = graph_id):
			raise UserNotAuthorized(request)
		if permission == 'GRAPH_UPDATE' and not graphs.controllers.is_user_authorized_to_update_graph(request, username=get_request_user(request), graph_id = graph_id):
			raise UserNotAuthorized(request)
		if permission == 'GRAPH_DELETE' and not graphs.controllers.is_user_authorized_to_delete_graph(request, username=get_request_user(request), graph_id = graph_id):
			raise UserNotAuthorized(request)
		if permission == 'GRAPH_SHARE' and not graphs.controllers.is_user_authorized_to_share_graph(request, username=get_request_user(request), graph_id = graph_id):
			raise UserNotAuthorized(request)
	if group_id is not None:
		if permission == 'GROUP_READ' and not users.controllers.is_user_authorized_to_view_group(request, username=get_request_user(request), group_id = group_id):
			raise UserNotAuthorized(request)
		if permission == 'GROUP_UPDATE' and not users.controllers.is_user_authorized_to_update_group(request, username=get_request_user(request), group_id = group_id):
			raise UserNotAuthorized(request)
		if permission == 'GROUP_DELETE' and not users.controllers.is_user_authorized_to_delete_group(request, username=get_request_user(request), group_id = group_id):
			raise UserNotAuthorized(request)
		if permission == 'GROUP_SHARE' and not users.controllers.is_user_authorized_to_share_with_group(request, username=get_request_user(request), group_id = group_id):
			raise UserNotAuthorized(request)
	if layout_id is not None:
		if permission == 'LAYOUT_READ' and not graphs.controllers.is_user_authorized_to_view_layout(request, username=get_request_user(request), layout_id = layout_id):
			raise UserNotAuthorized(request)
		if permission == 'LAYOUT_UPDATE' and not graphs.controllers.is_user_authorized_to_update_layout(request, username=get_request_user(request), layout_id = layout_id):
			raise UserNotAuthorized(request)
		if permission == 'LAYOUT_DELETE' and not graphs.controllers.is_user_authorized_to_delete_layout(request, username=get_request_user(request), layout_id = layout_id):
			raise UserNotAuthorized(request)
	return