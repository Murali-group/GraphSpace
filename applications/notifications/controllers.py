from datetime import datetime

from applications.notifications.models import *
import applications.notifications.dal as db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.database import *

from django.conf import settings


# Function to get notification count
def get_notification_count(request, owner_email=None, is_read=None):
    count = db.get_notification_count(
        request.db_session, owner_email=owner_email, is_read=is_read)
    return count

# Function to add owner notification to database
def add_owner_notification(message, type, resource, resource_id, owner_email=None, is_read=False, is_email_sent=False):
    sess = Database().session()
    notify = db.add_owner_notification(sess, message=message, type=type, owner_email=owner_email,
                                       resource=resource, resource_id=resource_id, is_read=is_read, is_email_sent=is_email_sent)
    # Apply changes to DB as the Middleware is not called
    sess.commit()
    return notify


# Function to add group notification to database
def add_group_notification(message, type, resource, resource_id, group_id=None, group_ids=[], owner_email=None, is_read=False, is_email_sent=False):
    sess = Database().session()
    if group_id is None:
        for gid in group_ids:
            notify = db.add_group_notification(sess, message=message, type=type, group_id=gid, resource=resource,
                                               resource_id=resource_id, owner_email=owner_email, is_read=is_read, is_email_sent=is_email_sent)
    else:
        notify = db.add_group_notification(sess, message=message, type=type, group_id=group_id, resource=resource,
                                           resource_id=resource_id, owner_email=owner_email, is_read=is_read, is_email_sent=is_email_sent)
    # Apply changes to DB as the Middleware is not called
    sess.commit()
    return notify


# Search for owner notification
def search_owner_notifications(request, owner_email=None, is_read=None, limit=20, offset=0):
    sort_attr = db.OwnerNotification.created_at
    orber_by = db.desc(sort_attr)

    total, notifications = db.find_owner_notifications(request.db_session,
                                                       owner_email=owner_email,
                                                       is_read=is_read,
                                                       limit=limit,
                                                       offset=offset,
                                                       order_by=orber_by)

    return total, notifications


# Search for group notification
def search_group_notifications(request, member_email, group_id=None, is_read=None, limit=20, offset=0):
    sort_attr = db.GroupNotification.created_at
    orber_by = db.desc(sort_attr)

    total, notifications = db.find_group_notifications(request.db_session,
                                                       member_email=member_email,
                                                       group_id=group_id,
                                                       is_read=is_read,
                                                       limit=limit,
                                                       offset=offset,
                                                       order_by=orber_by)

    return total, notifications


def read_owner_notifications(request, owner_email, notification_id=None):

    total, notify = db.read_owner_notifications(request.db_session,
                                                owner_email=owner_email,
                                                notification_id=notification_id)

    return total, notify


def read_group_notifications(request, member_email, group_id=None, notification_id=None):

    total, notify = db.read_group_notifications(request.db_session,
                                                member_email=member_email,
                                                group_id=group_id,
                                                notification_id=notification_id)

    return total, notify


# Get notification count per group for all groups
def get_notification_count_per_group(request, member_email, is_read=None):

    total, count_per_group = db.get_notification_count_per_group(request.db_session,
                                                                 member_email=member_email,
                                                                 is_read=is_read)

    return total, count_per_group
