from datetime import datetime

from applications.notifications.models import *
import applications.notifications.dal as db
from graphspace.exceptions import ErrorCodes, BadRequest
from graphspace.database import *

from django.conf import settings


def get_notification_count(request, owner_email=None, is_read=None):
    """    
    Function to get notification count

    :param request: HTTP Request
    :param owner_email: Email of the notification's user
    :param is_read: Read status
    :return: integer
    """
    count = db.get_notification_count(
        request.db_session, owner_email=owner_email, is_read=is_read)
    return count


def add_owner_notification(message, type, resource, resource_id, owner_email=None, is_read=False, is_email_sent=False):
    """
    Function to add owner notification to database

    :param message: Message of the notification.
    :param type: Type of the notification.
    :param resource: Resource type (graph,layout,group) of this notification.
    :param resource_id: Resource ID the notification is related to.
    :param owner_email: Email of the notification's owner.
    :param is_read: Check if notification is read or not.
    :param is_email_sent: Check if email has been sent for the notification or not.
    :return: OwnerNotification
    """
    db_session = Database().session()
    notify = db.add_owner_notification(db_session, message=message, type=type, owner_email=owner_email,
                                       resource=resource, resource_id=resource_id, is_read=is_read, is_email_sent=is_email_sent)
    # Apply changes to DB as the Middleware is not called
    db_session.commit()
    db_session.close()
    return notify


def add_group_notification(message, type, resource, resource_id, group_id=None, group_ids=[], owner_email=None, is_read=False, is_email_sent=False):
    """
    Add a new group notification.

    :param message: Message of the notification.
    :param type: Type of the notification.
    :param resource: Resource type (graph,layout,group) of this notification.
    :param resource_id: Resource ID the notification is related to.
    :param group_id: ID of the notification's group.
    :param owner_email: Email of user who created the notification.
    :param is_read: Check if notification is read or not.
    :param is_email_sent: Check if email has been sent for the notification or not.
    :return: list of GroupNotification
    """
    db_session = Database().session()
    if group_id is None:
        for gid in group_ids:
            notify = db.add_group_notification(db_session, message=message, type=type, group_id=gid, resource=resource,
                                               resource_id=resource_id, owner_email=owner_email, is_read=is_read, is_email_sent=is_email_sent)
    else:
        notify = db.add_group_notification(db_session, message=message, type=type, group_id=group_id, resource=resource,
                                           resource_id=resource_id, owner_email=owner_email, is_read=is_read, is_email_sent=is_email_sent)
    # Apply changes to DB as the Middleware is not called
    db_session.commit()
    db_session.close()
    return notify


# Search for owner notification
def search_owner_notifications(request, owner_email=None, is_read=None, limit=20, offset=0, is_bulk=False, created_at=None, first_created_at=None, resource=None, type=None):
    """
    Get list of owner notifications.

    :param request: HTTP request.
    :param message: Message of the notification.
    :param type: Type of the notification.
    :param resource: Resource type (graph,layout,group) of this notification.
    :param owner_email: Email of user who created the notification.
    :param is_read: Check if notification is read or not.
    :param limit: Number of notifications.
    :param offset: Offset from 1st notification.
    :param is_bulk: Indicator to show when to fetch as a bulk.
    :param created_at: Notification created_at datetime.
    :param first_created_at: First notification created at datetime in a group/cluster.
    :return: list of OwnerNotification
    """

    sort_attr = db.OwnerNotification.created_at
    orber_by = db.desc(sort_attr)

    total, notifications = db.find_owner_notifications(request.db_session,
                                                       owner_email=owner_email,
                                                       is_read=is_read,
                                                       limit=limit,
                                                       offset=offset,
                                                       is_bulk=is_bulk,
                                                       created_at=created_at,
                                                       first_created_at=first_created_at,
                                                       resource=resource,
                                                       type=type)

    return total, notifications


def search_group_notifications(request, member_email, group_id=None, is_read=None, limit=20, offset=0, is_bulk=False, created_at=None, first_created_at=None, resource=None, type=None):
    """
    Get list of group notifications.

    :param request: HTTP request.
    :param message: Message of the notification.
    :param type: Type of the notification.
    :param resource: Resource type (graph,layout,group) of this notification.
    :param owner_email: Email of user who created the notification.
    :param is_read: Check if notification is read or not.
    :param group_id: ID of the notification's group.
    :param limit: Number of notifications.
    :param offset: Offset from 1st notification.
    :param is_bulk: Indicator to show when to fetch as a bulk.
    :param created_at: Notification created_at datetime.
    :param first_created_at: First notification created at datetime in a group/cluster.
    :return: list of GroupNotification
    """
    sort_attr = db.GroupNotification.created_at
    orber_by = db.desc(sort_attr)

    total, notifications = db.find_group_notifications(request.db_session,
                                                       member_email=member_email,
                                                       group_id=group_id,
                                                       is_read=is_read,
                                                       limit=limit,
                                                       offset=offset,
                                                       is_bulk=is_bulk,
                                                       created_at=created_at,
                                                       first_created_at=first_created_at,
                                                       resource=resource,
                                                       type=type)

    return total, notifications


def read_owner_notifications(request, owner_email, resource=None, type=None, created_at=None, first_created_at=None, notification_id=None):
    """
    Mark owner notification as read

    :param request: HTTP request.
    :param owner_email: Email of user who created the notification.
    :param group_id: ID of the notification's group.
    :param notification_id: ID of notification
    :return: list of OwnerNotification
    """
    total, notify = db.read_owner_notifications(request.db_session,
                                                owner_email=owner_email,
                                                resource=resource,
                                                type=type,
                                                created_at=created_at,
                                                first_created_at=first_created_at,
                                                notification_id=notification_id)

    return total, notify


def read_group_notifications(request, member_email, group_id=None, resource=None, type=None, created_at=None, first_created_at=None, notification_id=None):
    """
    Mark group notification as read

    :param request: HTTP request.
    :param member_email: Email of user who created the notification.
    :param group_id: ID of the notification's group.
    :param notification_id: ID of notification
    :return: list of GroupNotification
    """
    total, notify = db.read_group_notifications(request.db_session,
                                                member_email=member_email,
                                                group_id=group_id,
                                                notification_id=notification_id)

    return total, notify


def get_notification_count_per_group(request, member_email, is_read=None):
    """
    Get notification count per group for all groups

    :param request: HTTP request.
    :param member_email: Email of user who created the notification.
    :param is_read: Check if notification is read or not.
    :return: list of Groups and count per group
    """
    total, count_per_group = db.get_notification_count_per_group(request.db_session,
                                                                 member_email=member_email,
                                                                 is_read=is_read)

    return total, count_per_group
