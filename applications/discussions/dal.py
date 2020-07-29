from sqlalchemy import and_, or_, desc, asc, event
from sqlalchemy.orm import joinedload, subqueryload
from graphspace.wrappers import with_session
from applications.discussions.models import *
from applications.users.models import *
from applications.comments.models import *
from applications.users.dal import *
import graphspace.signals as socket
from graphspace.database import *


@with_session
def add_discussion(db_session, topic, description, owner_email, group_id, is_closed=0):
    """
     Update discussion row entry.
     :param db_session: Database session.
     :param topic: Discussion topic
     :param description: Discussion description
     :param owner_email: Discussion owner_email
     :param group_id: Unique ID of the discussion
     :param is_closed: value for discussion status
     :return: Discussion if id exists else None
     """
    discussion = Discussion(topic=topic, description=description, owner_email=owner_email, group_id=group_id,
                            is_closed=is_closed)
    group = get_group(db_session, group_id)
    group.group_discussions.append(discussion)
    db_session.add(discussion)
    return discussion


@with_session
def get_discussions(db_session, group_id, keyword, limit, offset, order_by=desc(Discussion.created_at)):
    """
     Update discussion row entry.
     :param db_session: Database session.
     :param keyword: Search keyword
     :param group_id: Unique ID of the discussion
     :return: All related discussions and its count
     """
    query = db_session.query(Discussion).filter(Discussion.group_id == group_id)
    if order_by is not None:
        query = query.order_by(order_by)
    if keyword is not None:
        query1 = query.filter(Discussion.topic.ilike(keyword))
        query2 = query.filter(Discussion.owner_email.ilike(keyword))
        query3 = query.filter(Discussion.description.ilike(keyword))
        query4 = query1.union(query2)
        query = query3.union(query4)
    total = query.count()

    if offset is not None and limit is not None:
        query = query.limit(limit).offset(offset)

    return total, query.all()


@with_session
def close_discussion(db_session, id, updated_discussion):
    """
	Update discussion row entry.
	:param db_session: Database session.
	:param id: Unique ID of the discussion
	:param updated_discussion: Updated discussion row entry
	:return: Discussion if id exists else None
	"""
    discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
    query = db_session.query(Comment)
    query = query.options(joinedload('associated_discussion'))
    query = query.filter(Comment.discussion.any(CommentToDiscussion.discussion_id == id))
    for (key, value) in updated_discussion.items():
        setattr(discussion, key, value)
    for ele in query:
        for (key, value) in updated_discussion.items():
            setattr(ele, key, value)
    send_discussion(discussion, event="close")
    return discussion


@with_session
def reopen_discussion(db_session, id, updated_discussion):
    """
	Update discussion row entry.
	:param db_session: Database session.
	:param id: Unique ID of the discussion
	:param updated_discussion: Updated discussion row entry
	:return: Discussion if id exists else None
	"""
    discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
    query = db_session.query(Comment)
    query = query.options(joinedload('associated_discussion'))
    query = query.filter(Comment.discussion.any(CommentToDiscussion.discussion_id == id))
    for (key, value) in updated_discussion.items():
        setattr(discussion, key, value)
    for ele in query:
        for (key, value) in updated_discussion.items():
            setattr(ele, key, value)
    send_discussion(discussion, event="reopen")
    return discussion


@with_session
def delete_discussion(db_session, id):
    """
	Delete discussion from Discussion table.
	:param db_session: Database session.
	:param id: Unique ID of the discussion
	:return: discussion
	"""
    discussion = db_session.query(Discussion).filter(Discussion.id == id).one_or_none()
    query = db_session.query(Comment)
    query = query.options(joinedload('associated_discussion'))
    query = query.filter(Comment.discussion.any(CommentToDiscussion.discussion_id == id))
    for ele in query:
        db_session.delete(ele)
    db_session.delete(discussion)
    send_discussion(discussion, event="delete_discussion")
    return discussion


@with_session
def add_discussion_comment(db_session, text, owner_email, is_closed=0, parent_comment_id=None):
    """
    Get discussion by discussion id.
    :param db_session: Database session.\
    :param text: message of comment.
    :param owner_email: owner email of comment.
    :param is_closed: value for comment status.
    :param parent_comment_id: Unique ID of the parent comment
    :return: Discussion if id exists else None
    """
    comment = Comment(text=text, owner_email=owner_email, is_closed=is_closed, parent_comment_id=parent_comment_id)
    db_session.add(comment)
    # send_discussion(comment, event="insert_comment")
    return comment


@with_session
def add_comment_to_discussion(db_session, discussion_id, comment_id):
    """
    Adding discussion_id comment_id to comment_to_discussion table.
    :param db_session: Database session.
    :param discussion_id: Unique ID of the discussion
    :param comment_id: Unique ID of the comment
    :return: comment_to discussion row
    """
    comment_to_discussion = CommentToDiscussion(discussion_id=discussion_id, comment_id=comment_id)
    db_session.add(comment_to_discussion)
    return comment_to_discussion


@with_session
def get_discussion_by_id(db_session, id):
    """
	Get discussion by discussion id.
	:param db_session: Database session.
	:param id: Unique ID of the discussion
	:return: Discussion if id exists else None
	"""
    return db_session.query(Discussion).filter(Discussion.id == id).one_or_none()


def get_comments_by_discussion_id(db_session, group_id, discussion_id):
    """
    	Get comments vy discussion id
    	:param db_session: Database session.
    	:param group_id: Unique ID of the group
    	:param discussion_id: Unique ID of the discussion
    	:return: total comments value and comments if id exists else None
    	"""
    query = db_session.query(Comment)
    query = query.options(joinedload('associated_discussion'))
    query = query.filter(Comment.discussion.any(CommentToDiscussion.discussion_id == discussion_id))
    return query.count(), query.all()


@with_session
def update_comment(db_session, id, updated_comment):
    """
	Update comment row entry.
	:param db_session: Database session.
	:param id: Unique ID of the discussion
	:param updated_comment: Updated comment row entry
	:return: Comment if id exists else None
	"""
    comment = db_session.query(Comment).filter(Comment.id == id).one_or_none()
    for (key, value) in updated_comment.items():
        setattr(comment, key, value)
    send_comment(comment, event="update_comment")
    return comment


@with_session
def delete_comment(db_session, id):
    """
	Delete comment from Comment table.
	:param db_session: Database session.
	:param id: Unique ID of the comment
	:return: comment
	"""
    comment = db_session.query(Comment).filter(Comment.id == id).one_or_none()
    db_session.delete(comment)
    send_comment(comment, event="delete_comment")
    return comment


def send_comment(comment, event):
    users_list = get_users_by_group(Database().session(), comment.associated_discussion[0].discussion.group_id)
    socket.send_discussion(discussion=comment, type="private", users=users_list, event=event)


def send_discussion(discussion, event):
    users_list = get_users_by_group(Database().session(), discussion.group_id)
    socket.send_discussion(discussion=discussion, type="private", users=users_list, event=event)
