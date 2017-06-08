from datetime import datetime

from applications.notifications.models import *
from graphspace.exceptions import ErrorCodes, BadRequest

from django.conf import settings
from graphspace.database import *


# Function to add notification to database
def add_notification(message, type, graph_id, owner_email=None, group_id=None, status='new'):
    db = Database()
    notify = Notification(message=message, type=type, owner_email=owner_email,
                          group_id=group_id, status=status, graph_id=graph_id)
    with db.session_scope() as sess:
        sess.add(notify)
    return notify
