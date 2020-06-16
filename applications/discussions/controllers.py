from sqlalchemy.exc import IntegrityError
import applications.discussions.dal as db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.wrappers import atomic_transaction


@atomic_transaction
def add_discussion(request, message=None, topic=None, group_id=None, is_resolved=0, owner_email=None,
                   parent_discussion_id=None):
    # Construct new discussion to add to database
    discussion = db.add_discussion(request.db_session, message=message, topic=topic,
                                   owner_email=owner_email,
                                   group_id=group_id, is_resolved=is_resolved,
                                   parent_discussion_id=parent_discussion_id)
    return discussion

def search_discussions_by_group_id(request, group_id=None):
    if group_id is None:
        raise Exception("Atleast one group id is required.")
    return db.get_discussions_by_group_id(request.db_session, group_id=group_id)

def get_discussion_by_id(request, discussion_id):
    return db.get_discussion(request.db_session, id=discussion_id)

def search_comments_by_discussion_id(request, group_id=None, discussion_id=None):
    if group_id is None:
        raise Exception("Atleast one group id is required.")
    if discussion_id is None:
        raise Exception("Atleast one discussion id is required.")
    return db.get_comments_by_discussion_id(request.db_session, group_id=group_id, discussion_id=discussion_id)