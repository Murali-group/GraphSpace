from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import joinedload, subqueryload

from applications.notifications.models import *
from graphspace.wrappers import with_session


@with_session
def add_notification(db_session, message, type, graph_id, owner_email=None, group_id=None, status='new'):
    """
    Add a new notification.

    :param db_session: Database session.
    :param message: Message of the notification.
    :param type: Type of the notification.
    :param status: Status of the notification.
    :param graph_id: Graph ID of the graph the notification is related to.
    :param owner_email: Email of the notification's user.
    :return: Notification
    """
    notify = Notification(message=message, type=type, graph_id=graph_id,
                          owner_email=owner_email, group_id=group_id, status=status)
    db_session.add(notify)
    return notify


@with_session
def find_notifications(db_session, owner_email, status, type, limit, offset, order_by=asc(Notification.created_at)):
    query = db_session.query(Notification)

    if order_by is not None:
        query = query.order_by(order_by)

    if owner_email is not None:
        query = query.filter(Notification.owner_email.ilike(owner_email))

    if status is not None:
        query = query.filter(Notification.status.ilike(status))

    if type is not None:
        query = query.filter(Notification.type.ilike(type))

    total = query.count()

    if offset is not None and limit is not None:
        query = query.limit(limit).offset(offset)

    return total, query.all()
