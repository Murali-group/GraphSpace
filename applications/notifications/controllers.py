from datetime import datetime

from applications.notifications.models import *
import applications.notifications.dal as db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.database import *

from django.conf import settings


# Function to add notification to database
def add_notification(message, type, graph_id, owner_email=None, group_id=None, status='new'):
    sess = Database().session()
    notify = db.add_notification(sess, message=message, type=type, owner_email=owner_email,
                                 group_id=group_id, status=status, graph_id=graph_id)
    # Apply changes to DB as the Middleware is not called
    sess.commit()
    return notify


def search_notifications(request, owner_email=None, status=None, type=None, limit=20, offset=0):
    sort_attr = db.Notification.created_at
    orber_by = db.desc(sort_attr)

    total, notifications = db.find_notifications(request.db_session,
                                                 owner_email=owner_email,
                                                 status=status,
                                                 type=type,
                                                 limit=limit,
                                                 offset=offset,
                                                 order_by=orber_by)

    return total, notifications
