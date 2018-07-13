from sqlalchemy.exc import IntegrityError
import applications.comments.dal as db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.wrappers import atomic_transaction

@atomic_transaction
def add_comment(request, message=None, graph_id=None, edges=None, nodes=None, is_resolved=0, owner_email=None,
			 parent_comment_id=None, layout_id=None):

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

	return comment

def get_comment_by_graph_id(request, graph_id):
	return db.get_comment_by_graph_id(request.db_session, graph_id=graph_id)

@atomic_transaction
def edit_comment(request, comment_id=None, message=None, is_resolved=None):

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
	return db.delete_comment(request.db_session, id=id)
