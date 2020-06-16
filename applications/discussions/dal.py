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
def get_discussions_by_group_id(db_session, group_id):
	query = db_session.query(Discussion).filter(Discussion.group_id == group_id)
	query = query.filter(Discussion.parent_discussion_id == None)
	return query.count(), query.all()

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


@event.listens_for(Discussion, 'after_insert')
def update_listener(mapper, connection, discussion):
	send_discussion(discussion, event="insert")

def send_discussion(discussion, event):
	users_list = get_users_by_group(Database().session(), discussion.group_id)
	socket.send_discussion(discussion=discussion, type="private", users=users_list, event=event)

