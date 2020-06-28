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


def search_discussions_by_group_id(request, group_id=None, topic=None, limit=20, offset=0, order='desc', sort='created_at'):
    if group_id is None:
        raise Exception("Atleast one group id is required.")

    if sort == 'topic':
        sort_attr = db.Discussion.topic
    else:
        sort_attr = db.Discussion.created_at

    if order == 'desc':
        orber_by = db.asc(sort_attr)
    else:
        orber_by = db.desc(sort_attr)

    total, discussions = db.get_discussions_by_group_id(request.db_session,
                                                        group_id=group_id,
                                                        topic=topic,
                                                        limit=limit,
                                                        offset=offset,
                                                        order_by=orber_by)

    return total, discussions



def get_discussion_by_id(request, discussion_id):
    return db.get_discussion(request.db_session, id=discussion_id)


def search_comments_by_discussion_id(request, group_id=None, discussion_id=None):
    if group_id is None:
        raise Exception("Atleast one group id is required.")
    if discussion_id is None:
        raise Exception("Atleast one discussion id is required.")
    return db.get_comments_by_discussion_id(request.db_session, group_id=group_id, discussion_id=discussion_id)


def is_user_authorized_to_delete_discussion(request, username, discussion_id):
    is_authorized = False

    discussion = db.get_discussion(request.db_session, discussion_id)

    if discussion is not None:  # Graph exists
        if discussion.owner_email == username:
            is_authorized = True

    return is_authorized


def delete_discussion_by_id(request, discussion_id):
    db.delete_discussion(request.db_session, id=discussion_id)
    return


def update_discussion(request, discussion_id, message, is_resolved):
    discussion = {}
    if message is not None:
        discussion['message'] = message
        return db.update_discussion(request.db_session, id=discussion_id, updated_discussion=discussion)
    if is_resolved is not None:
        if is_resolved == u'1':
            discussion['is_resolved'] = is_resolved
            return db.resolve_discussion(request.db_session, id=discussion_id, updated_discussion=discussion)
        if is_resolved == u'0':
            discussion['is_resolved'] = is_resolved
            return db.reopen_discussion(request.db_session, id=discussion_id, updated_discussion=discussion)
