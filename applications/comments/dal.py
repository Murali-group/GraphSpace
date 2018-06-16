from sqlalchemy import and_, or_, desc, asc, event
from sqlalchemy.orm import joinedload, subqueryload
from graphspace.wrappers import with_session
from applications.comments.models import *
from applications.graphs.dal import *
from applications.users.models import *
import graphspace.signals as socket
from graphspace.database import *

@with_session
def add_comment(db_session, message, graph_id, owner_email=None, is_resolved=0, layout_id=None, parent_comment_id=None):
	comment = Comment(owner_email=owner_email, graph_id=graph_id, layout_id=layout_id,
				  is_resolved=is_resolved, parent_comment_id=parent_comment_id, message=message)
	graph = get_graph_by_id(db_session, graph_id)
	graph.comments.append(comment)
	db_session.add(comment)
	return comment

@with_session
def add_comment_to_edge(db_session, comment_id, edge_id):
	comment_to_edge = CommentToEdge(comment_id=comment_id, edge_id=edge_id)
	db_session.add(comment_to_edge)
	return comment_to_edge

@with_session
def add_comment_to_node(db_session, comment_id, node_id):
	comment_to_node = CommentToNode(comment_id=comment_id, node_id=node_id)
	db_session.add(comment_to_node)
	return comment_to_node

@with_session
def get_comment_by_graph_id(db_session, graph_id):
	query = db_session.query(Comment).filter(Comment.graph_id == graph_id)
	return query.count(), query.all()

@with_session
def get_user_emails_by_graph_id(db_session, graph_id):
	query = db_session.query(Comment, User, GroupToGraph, GroupToUser)
	query = query.filter(Comment.graph_id == graph_id)
	query = query.filter(GroupToGraph.graph_id == graph_id)
	query = query.filter(GroupToUser.group_id == GroupToGraph.group_id)
	query = query.filter(User.id == GroupToUser.user_id)
	return query.all()

@event.listens_for(Comment, 'after_insert')
def send_comment(mapper, connection, comment):
	users_list = get_user_emails_by_graph_id(Database().session(), comment.serialize()['graph_id'])
	if comment.graph.is_public == 0:
		socket.send_comment(comment=comment, type="private", users=users_list)
	else:
		socket.send_comment(comment=comment, type="public")