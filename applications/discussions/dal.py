from sqlalchemy import and_, or_, desc, asc, event
from sqlalchemy.orm import joinedload, subqueryload
from graphspace.wrappers import with_session
from applications.discussions.models import *
from applications.users.dal import *
from applications.users.models import *
import graphspace.signals as socket
from graphspace.database import *

@with_session
def add_discussion(db_session, message, topic, group_id, owner_email=None, is_resolved=0, parent_discussion_id=None):
	discussion = Discussion(owner_email=owner_email, group_id=group_id,
				  is_resolved=is_resolved, parent_discussion_id=parent_discussion_id, message=message, topic=topic)
	group = get_group(db_session, group_id)
	group.group_discussions.append(discussion)
	db_session.add(discussion)
	return discussion


@with_session
def get_discussions_by_group_id(db_session, group_id, topic, limit, offset, order_by=desc(Discussion.created_at)):
	# query = db_session.query(Group)
	#
	# if order_by is not None:
	# 	query = query.order_by(order_by)
	#
	# if owner_email is not None:
	# 	query = query.filter(Group.owner_email.ilike(owner_email))
	#
	# if name is not None:
	# 	query = query.filter(Group.name.ilike(name))
	#
	# if description is not None:
	# 	query = query.filter(Group.description.ilike(description))
	#
	# if member_email is not None:
	# 	query = query.options(joinedload('member_users'))
	# 	query = query.filter(Group.members.any(User.email == member_email))
	#
	# if graph_ids is not None and len(graph_ids) > 0:
	# 	query = query.options(joinedload('shared_graphs'))
	# 	query = query.filter(Group.graphs.any(Graph.id.in_(graph_ids)))
	#
	# total = query.count()
	#
	# if offset is not None and limit is not None:
	# 	query = query.limit(limit).offset(offset)
	#
	# return total, query.all()

	query = db_session.query(Discussion).filter(Discussion.group_id == group_id)
	query = query.filter(Discussion.parent_discussion_id == None)
	if order_by is not None:
		query = query.order_by(order_by)
	if topic is not None:
		query1 = query.filter(Discussion.topic.ilike(topic))
		query2 = query.filter(Discussion.owner_email.ilike(topic))
		query3 = query.filter(Discussion.message.ilike(topic))
		query4 = query1.union(query2)
		query = query3.union(query4)
	# query = query.filter(Discussion.topic.ilike(topic))
	# query2 = query.filter(Discussion.owner_email.ilike('%wano%'))
	# query = query1.union(query2)
	# query = query.order_by(desc(Discussion.created_at))
	total = query.count()

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()
	# return query.count(), query.all()

@with_session
def get_discussion(db_session, id):
	"""
	Get group by group id.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:return: Group if id exists else None
	"""
	return db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
def get_comments_by_discussion_id(db_session, group_id, discussion_id):
	query = db_session.query(Discussion).filter(Discussion.group_id == group_id)
	query = query.filter(Discussion.parent_discussion_id == discussion_id)
	return query.count(), query.all()

@with_session
def delete_discussion(db_session, id):
	"""
	Delete group from Group table.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:return: None
	"""
	discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
	query = db_session.query(Discussion).filter(Discussion.parent_discussion_id == id).all()
	db_session.delete(discussion)
	for ele in query:
		db_session.delete(ele)
	return discussion

@with_session
def update_discussion(db_session, id, updated_discussion):
	"""
	Update group row entry.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:param updated_group: Updated group row entry
	:return: Group if id exists else None
	"""
	discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
	for (key, value) in updated_discussion.items():
		setattr(discussion, key, value)
	send_discussion(discussion, event="edited")
	return discussion

@with_session
def resolve_discussion(db_session, id, updated_discussion):
	"""
	Update group row entry.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:param updated_group: Updated group row entry
	:return: Group if id exists else None
	"""
	discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
	for (key, value) in updated_discussion.items():
		setattr(discussion, key, value)
	send_discussion(discussion, event="resolve")
	return discussion

@with_session
def reopen_discussion(db_session, id, updated_discussion):
	"""
	Update group row entry.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:param updated_group: Updated group row entry
	:return: Group if id exists else None
	"""
	discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
	for (key, value) in updated_discussion.items():
		setattr(discussion, key, value)
	send_discussion(discussion, event="reopen")
	return discussion


@event.listens_for(Discussion, 'after_insert')
def update_listener(mapper, connection, discussion):
	send_discussion(discussion, event="insert")

@event.listens_for(Discussion, 'after_delete')
def delete_listener(mapper, connection, discussion):
	send_discussion(discussion, event="delete")

def send_discussion(discussion, event):
	users_list = get_users_by_group(Database().session(), discussion.group_id)
	socket.send_discussion(discussion=discussion, type="private", users=users_list, event=event)

