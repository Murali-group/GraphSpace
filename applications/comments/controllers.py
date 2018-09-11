from sqlalchemy.exc import IntegrityError
import applications.comments.dal as db
import applications.graphs.dal as graphs_db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.wrappers import atomic_transaction

@atomic_transaction
def add_comment(request, message=None, graph_id=None, edges=None, nodes=None, is_resolved=0, owner_email=None,
			 parent_comment_id=None, layout_id=None):
	"""

	Parameters
	----------
	request: object
		HTTP Request.
	message: string
		Comment message.
	graph_id: Integer
		Unique ID of each graph.
	edges: List
		List of edge names on associated with the comment.
	nodes: List
		List of node names on associated with the comment.
	is_resolved: Integer
		Integer indicating if the comment is resolved or not.
	owner_email: string
		Email ID of user who comment on the graph.
	parent_comment_id: Integer
		Unique ID of parent comment.
	layout_id: Integer
		Unique ID of layout.

	Returns
	-------
	comment: Object
		Comment Object.

	"""
	# Construct new comment to add to database
	comment = db.add_comment(request.db_session, message=message, owner_email=owner_email,
	                         graph_id=graph_id, layout_id=layout_id, is_resolved=is_resolved,
	                         parent_comment_id=parent_comment_id)
	# Add comment edges
	if edges != None:
		for edge_id in edges:
			db.add_comment_to_edge(request.db_session, comment_id=comment.id, edge_id=edge_id)

	# Add comment nodes
	if nodes != None:
		for node_id in nodes:
			db.add_comment_to_node(request.db_session, comment_id=comment.id, node_id=node_id)

	db.send_comment(comment, event="insert")
	return comment

@atomic_transaction
def pin_comment(request, comment_id=None, owner_email=None):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.
	owner_email: string
		Email ID of user who comment on the graph.

	Returns
	-------
	pin_comment: Object.
		PinComment Object.

	"""
	# Pin comment
	comment = get_comment_by_id(request, comment_id=comment_id)
	if comment.parent_comment_id != None:
		raise BadRequest(request, error_code=ErrorCodes.Validation.UserCannotPinThisComment)
	pin_comment = db.pin_comment(request.db_session, comment_id=comment_id, owner_email=owner_email)
	return pin_comment

@atomic_transaction
def unpin_comment(request, comment_id=None, owner_email=None):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.
	owner_email: string
		Email ID of user who comment on the graph.

	Returns
	-------
	unpin_comment: Object.
		Deleted PinComment Object.

	"""
	# Pin comment
	comment = get_comment_by_id(request, comment_id=comment_id)
	if comment.parent_comment_id != None:
		raise BadRequest(request, error_code=ErrorCodes.Validation.UserCannotUnpinThisComment)
	unpin_comment = db.unpin_comment(request.db_session, comment_id=comment_id, owner_email=owner_email)
	return unpin_comment

def get_comment_by_graph_id(request, graph_id):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	graph_id: Integer
		Unique ID of graph.

	Returns
	-------
	return value: Object.
		Comment Object.

	"""
	return db.get_comment_by_graph_id(request.db_session, graph_id=graph_id)

def get_pinned_comments(request, comment_id, owner_email):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.
	owner_email: Integer
		Email ID of user.

	Returns
	-------
	return value: List.
		List of PinComment Objects.

	"""
	return db.get_pinned_comments(request.db_session, comment_id=comment_id, owner_email=owner_email)

def get_nodes_by_comment_id(request, comment_id):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.

	Returns
	-------
	return value: List.
		List of Node Objects.

	"""
	return db.get_nodes_by_comment_id(request.db_session, comment_id=comment_id)

def get_edges_by_comment_id(request, comment_id):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.

	Returns
	-------
	return value: List.
		List of Edge Objects.

	"""
	return db.get_edges_by_comment_id(request.db_session, comment_id=comment_id)

def get_comment_by_id(request, comment_id):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.

	Returns
	-------
	return value: object.
		Comment Object.

	"""
	return db.get_comment_by_id(request.db_session, id=comment_id)

@atomic_transaction
def edit_comment(request, comment_id=None, message=None, is_resolved=None):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	comment_id: Integer
		Unique ID of comment.
	message: String
		New comment message.
	is_resolved: Integer
		Indicates if the comment is resolved or not.

	Returns
	-------
	return value: object
		Edited Comment Object.

	"""
	updated_comment = {}
	
	# Check if field is present or not.
	if is_resolved != None:
		updated_comment['is_resolved'] = is_resolved
	if message != None:
		updated_comment['message'] = message

	# Only top comment in a comment thread can be resolved.
	comment = db.get_comment_by_id(request.db_session, id=comment_id)
	if comment.serialize()['is_resolved'] == 0 and is_resolved == 1 and comment.serialize()['parent_comment_id'] != None:
		raise Exception('Reply comments can not be resolved')

	return db.update_comment(request.db_session, id=comment_id, updated_comment=updated_comment)

@atomic_transaction
def delete_comment(request, id=None):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	id: Integer
		Unique ID of comment.

	Returns
	-------
	return value: object
		Deleted Comment Object.

	"""
	return db.delete_comment(request.db_session, id=id)

def is_user_authorized_to_update_comment(request, username, comment_id):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	username: string
		Email ID of user.
	comment_id: integer
		Unique ID of comment.

	Returns
	-------
	is_authorized: bool
		Returns True if the user is authorized to update comment else False.

	"""
	is_authorized = False
	comment = db.get_comment_by_id(request.db_session, comment_id)

	if comment is not None:  # Comment exists
		if comment.owner_email == username:
			is_authorized = True

	return is_authorized

def is_user_authorized_to_delete_comment(request, username, comment_id):
	"""

	Parameters
	----------
	request: object
		HTTP request.
	username: string
		Email ID of user.
	comment_id: integer
		Unique ID of comment.

	Returns
	-------
	is_authorized: bool
		Returns True if the user is authorized to delete comment else False.

	"""
	is_authorized = False

	comment = db.get_comment_by_id(request.db_session, comment_id)
	if comment is not None:
		graph = graphs_db.get_graph_by_id(request.db_session, comment.graph_id)

	if comment is not None:  # Comment exists
		if comment.owner_email == username:
			is_authorized = True
		elif graph.owner_email == username:
			is_authorized = True

	return is_authorized