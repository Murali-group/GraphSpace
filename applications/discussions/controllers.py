from sqlalchemy.exc import IntegrityError
import applications.discussions.dal as db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.wrappers import atomic_transaction


@atomic_transaction
def add_discussion(request, topic=None, description=None, owner_email=None, group_id=None, is_closed=0):
    # Construct new discussion to add to database
    discussion = db.add_discussion(request.db_session, topic=topic, description=description,
                                   owner_email=owner_email,
                                   group_id=group_id, is_closed=is_closed)
    return discussion


def get_discussions(request, group_id=None, keyword=None, limit=20, offset=0, order='desc', sort='created_at'):
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

    total, discussions = db.get_discussions(request.db_session,
                                            group_id=group_id,
                                            keyword=keyword,
                                            limit=limit,
                                            offset=offset,
                                            order_by=orber_by)

    return total, discussions


def update_discussion(request, discussion_id, is_closed):
    discussion = {}
    if is_closed is not None:
        if is_closed == u'1':
            discussion['is_closed'] = is_closed
            return db.close_discussion(request.db_session, id=discussion_id, updated_discussion=discussion)
        if is_closed == u'0':
            discussion['is_closed'] = is_closed
            return db.reopen_discussion(request.db_session, id=discussion_id, updated_discussion=discussion)


def delete_discussion_by_id(request, discussion_id):
    db.delete_discussion(request.db_session, id=discussion_id)
    return


def get_discussion_by_id(request, discussion_id):
    return db.get_discussion_by_id(request.db_session, id=discussion_id)


def is_user_authorized_to_delete_discussion(request, username, discussion_id):
    is_authorized = False

    discussion = db.get_discussion_by_id(request.db_session, discussion_id)

    if discussion is not None:
        if discussion.owner_email == username:
            is_authorized = True

    return is_authorized


def add_discussion_comment(request, discussion_id=None, text=None, owner_email=None, is_closed=0):
    # Construct new comment to add to database
    comment = db.add_discussion_comment(request.db_session, text=text, owner_email=owner_email, is_closed=is_closed)
    comment_to_discussion = db.add_comment_to_discussion(request.db_session, discussion_id=discussion_id,
                                                         comment_id=comment.id)
    db.send_comment(comment, event="insert_comment")
    return comment


def search_comments_by_discussion_id(request, group_id=None, discussion_id=None):
    if group_id is None:
        raise Exception("Atleast one group id is required.")
    if discussion_id is None:
        raise Exception("Atleast one discussion id is required.")
    return db.get_comments_by_discussion_id(request.db_session, group_id=group_id, discussion_id=discussion_id)


def update_comment(request, text, comment_id):
    comment = {}
    if text is not None:
        comment['text'] = text
    return db.update_comment(request.db_session, id=comment_id, updated_comment=comment)


def delete_comment_by_id(request, comment_id):
    db.delete_comment(request.db_session, id=comment_id)
    return


def add_comment_reaction(request, comment_id=None, content=None, owner_email=None):
    # Construct new comment to add to database
    reaction = db.add_comment_reaction(request.db_session, content=content, owner_email=owner_email)
    comment_to_reaction = db.add_comment_to_reaction(request.db_session, comment_id=comment_id, reaction_id=reaction.id)
    return reaction


def delete_comment_reaction(request, comment_id=None, content=None, owner_email=None):
    # Construct new comment to add to database
    reaction = db.delete_comment_reaction(request.db_session, comment_id=comment_id, content=content,
                                          owner_email=owner_email)


def get_comment_reactions(request, comment_id=None, content=None):
    # Construct new comment to add to database
    total, reactions = db.get_comment_reactions(request.db_session, comment_id=comment_id, content=content)
    return total, reactions
