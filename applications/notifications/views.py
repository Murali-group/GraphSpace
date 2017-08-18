import json

import applications.notifications.controllers as notification_controllers
import applications.graphs.controllers as graph_controllers
import applications.users.controllers as user_controllers
import graphspace.authorization as authorization
import graphspace.utils as utils
from django.conf import settings
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.template import RequestContext
from graphspace.wrappers import is_authenticated
from graphspace.exceptions import MethodNotAllowed, BadRequest, ErrorCodes
from graphspace.utils import get_request_user


@is_authenticated(redirect_url='/')
def notifications_page(request):
    """
            Wrapper view function for the following pages:
            /notifications/

            Parameters
            ----------
            request : HTTP Request

            Returns
            -------
            response : HTML Page Response
                    Rendered notifications list page in HTML.

            Raises
            ------
            MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

            Notes
            ------
    """
    if 'GET' == request.method:
        context = RequestContext(request, {
            "status": request.GET.get('status', '')
        })
        return render(request, 'notifications/index.html', context)
    else:
        # Handle other type of request methods like POST, PUT, UPDATE.
        raise MethodNotAllowed(request)


@is_authenticated(redirect_url='/')
def notifications_count(request):
    """
            Wrapper view function for the following pages:
            /notifications/count

            Parameters
            ----------
            request : HTTP Request

            Returns
            -------
            response : JSON response

            Raises
            ------
            MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

            Notes
            ------
    """
    query = request.GET
    is_read = query.get('is_read', None)

    if is_read == 'true':
        is_read = True
    elif is_read == 'false':
        is_read = False
    else:
        is_read = None

    return HttpResponse(json.dumps({"count": notification_controllers.get_notification_count(request,
                                                                                             owner_email=query.get(
                                                                                                 'owner_email', None),
                                                                                             is_read=is_read)}),
                        content_type="application/json",
                        status=200)


@is_authenticated(redirect_url='/')
def notifications_ajax_api(request, notification_id=None):
    """
    Handles any request sent to following urls:
            /ajax/notifications

    Parameters
    ----------  
    request - HTTP Request

    Returns
    -------
    response : JSON Response

    """
    return _notifications_api(request, notification_id=notification_id)


@is_authenticated(redirect_url='/')
def notifications_read(request, notification_id=None):
    """
    Handles any request sent to following urls:
            /ajax/notifications/read
            /ajax/notifications/read/<notification-id>

    Parameters
    ----------
    request - HTTP Request

    Returns
    -------
    response : JSON Response

    """
    return _notifications_api(request, notification_id=notification_id)


@is_authenticated(redirect_url='/')
def notification_redirect(request, notification_id):
    """
    Handles any request sent to following urls:
            /notification/<notification-id>/redirect/<resource>/<resource-id>

    Parameters
    ----------
    request - HTTP Request

    Returns
    -------
    response : JSON Response

    """
    query = request.GET
    topic = query.get('topic', None)
    owner_email = query.get('owner_email', None)
    # Validate get notifications API request
    user_role = authorization.user_role(request)
    if user_role == authorization.UserRole.LOGGED_IN:
        if get_request_user(request) != owner_email:
            raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedNotificationAccess,
                             args=get_request_user(request))
    if topic == 'owner':
        message, notify = notification_controllers.read_owner_notifications(request,
                                                                            owner_email=owner_email,
                                                                            notification_id=notification_id
                                                                            )
        notify = utils.serializer(notify)
    elif topic == 'group':
        message, notify = notification_controllers.read_group_notifications(request,
                                                                            member_email=owner_email,
                                                                            notification_id=notification_id)
        notify = utils.serializer(notify)
    else:
        raise BadRequest(
            request, error_code=ErrorCodes.Validation.BadRequest, args=get_request_user(request))

    url = '/{resource}/{resource_id}'.format(**notify)
    resource = notify.get('resource', None)
    resource_id = notify.get('resource_id', None)
    if resource == 'layout':
        return_value = utils.serializer(
            graph_controllers.get_layout_by_id(request, layout_id=resource_id, include_deleted=True))
        if return_value is not None:
            if return_value.get('is_deleted', False):
                url = '/graphs/{graph_id}'.format(**return_value)
            else:
                url = '/graphs/{graph_id}?user_layout={id}'.format(
                    **return_value)
    elif resource == 'graph':
        return_value = graph_controllers.get_graph_by_id(request, resource_id)
    elif resource == 'group':
        return_value = user_controllers.get_group_by_id(request, resource_id)
    else:
        return_value = None
    if return_value is None:
        url = '/notifications'
    return redirect(url)


def _notifications_api(request, notification_id=None):
    """
    Handles any request (GET/POST) sent to /notifications or notifications/<notification_id>

    Parameters
    ----------
    request - HTTP Request

    Returns
    -------

    """
    if request.META.get('HTTP_ACCEPT', None) == 'application/json':
        if request.method == "GET" and notification_id is None:
            return HttpResponse(json.dumps(_get_notifications(request, query=request.GET)), content_type="application/json")
        elif request.method == "PUT":
            return HttpResponse(json.dumps(_update_notifications_read(
                request,
                notification_id=notification_id,
                query=QueryDict(request.body))
            ),
                content_type="application/json",
                status=200)
        else:
            # Handle other type of request methods like OPTIONS etc.
            raise MethodNotAllowed(request)
    else:
        raise BadRequest(request)


def _get_notifications(request, query={}):
    """

    Query Parameters
    ----------
    owner_email : string
            Email of the Owner of the notification.
    is_read: string
            Status of the notification [new, read].
    limit : integer
            Number of entities to return. Default value is 20.
    offset : integer
            Offset the list of returned entities by this number. Default value is 0.
    topic : string
            Type of the notification [owner, group, watching].
    is_bulk: string
            Identify if notifications should be grouped
    created_at: string
            Timestamp of the latest notification in a group
    first_created_at: string
            Timestamp of the oldest notification in a group
    resource: string
            Type of resource [group, layout, graph]
    type: string
            Type of the notification [create, update, delete]

    Parameters
    ----------
    query : dict
            Dictionary of query parameters.
    request : object
            HTTP GET Request.
    owner_email : string
            Email of the Owner of the notification.

    Returns
    -------
    total : integer
            Number of notifications matching the request.
    notifications : List of Notifications.
            List of Notification Objects with given limit and offset.

    Raises
    ------

    Notes
    ------

    """

    # Validate get notifications API request
    user_role = authorization.user_role(request)
    if user_role == authorization.UserRole.LOGGED_IN:
        if get_request_user(request) != query.get('owner_email', None):
            raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedNotificationAccess,
                             args=get_request_user(request))

    topic = query.get('topic', None)
    is_read = query.get('is_read', None)

    # this will be true if we need all notifications without combining it
    is_bulk = query.get('is_bulk', None)

    if is_read == 'true':
        is_read = True
    elif is_read == 'false':
        is_read = False
    else:
        is_read = None

    # There are two data types returned depending on is_bulk condition
    if is_bulk == 'true':
        is_bulk = True
        serializer = utils.serializer
    else:
        is_bulk = False
        serializer = utils.owner_notification_bulk_serializer if topic == 'owner' else utils.group_notification_bulk_serializer

    if topic == 'owner':
        total, notifications = notification_controllers.search_owner_notifications(request,
                                                                                   owner_email=query.get(
                                                                                       'owner_email', None),
                                                                                   is_read=is_read,
                                                                                   limit=query.get(
                                                                                       'limit', 20),
                                                                                   offset=query.get(
                                                                                       'offset', 0),
                                                                                   created_at=query.get(
                                                                                       'created_at', None),
                                                                                   first_created_at=query.get(
                                                                                       'first_created_at', None),
                                                                                   resource=query.get(
                                                                                       'resource', None),
                                                                                   type=query.get(
                                                                                       'type', None),
                                                                                   is_bulk=is_bulk)

        notifications = [serializer(notify) for notify in notifications]

    elif topic == 'group':
        total, notifications = notification_controllers.search_group_notifications(request,
                                                                                   member_email=query.get(
                                                                                       'owner_email', None),
                                                                                   group_id=query.get(
                                                                                       'group_id', None),
                                                                                   is_read=is_read,
                                                                                   limit=query.get(
                                                                                       'limit', 20),
                                                                                   offset=query.get(
                                                                                       'offset', 0),
                                                                                   created_at=query.get(
                                                                                       'created_at', None),
                                                                                   first_created_at=query.get(
                                                                                       'first_created_at', None),
                                                                                   resource=query.get(
                                                                                       'resource', None),
                                                                                   type=query.get(
                                                                                       'type', None),
                                                                                   is_bulk=is_bulk)
        notifications = [serializer(notify) for notify in notifications]

    else:
        raise BadRequest(
            request, error_code=ErrorCodes.Validation.BadRequest, args=get_request_user(request))

    return {
        'total': total,
        'notifications': notifications
    }


def _update_notifications_read(request, notification_id=None, query={}):
    """

    Query Parameters
    ----------
    owner_email : string
            Email of the Owner of the notification.
    topic : string
            Type of the notification [owner, group, watching].
    type : string
            Type of the notification [create, update, delete]
    created_at: string
            Timestamp of the latest notification in a group
    first_created_at: string
            Timestamp of the oldest notification in a group
    resource : string
            Type of resource [group, layout, graph]

    Parameters
    ----------
    query : dict
            Dictionary of query parameters.
    request : object
            HTTP GET Request.
    owner_email : string
            Email of the Owner of the notification.

    Returns
    -------
    message : Message that notifications/notification has been marked read.

    Raises
    ------

    Notes
    ------

    """

    # Validate get notifications API request
    user_role = authorization.user_role(request)
    if user_role == authorization.UserRole.LOGGED_IN:
        if get_request_user(request) != query.get('owner_email', None):
            raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedNotificationAccess,
                             args=get_request_user(request))

    topic = query.get('topic', None)

    if topic == 'owner':
        total, notify = notification_controllers.read_owner_notifications(request,
                                                                          owner_email=query.get(
                                                                              'owner_email', None),
                                                                          resource=query.get(
                                                                              'resource', None),
                                                                          created_at=query.get(
                                                                              'created_at', None),
                                                                          first_created_at=query.get(
                                                                              'first_created_at', None),
                                                                          type=query.get(
                                                                              'type', None),
                                                                          notification_id=notification_id
                                                                          )
    elif topic == 'group':
        total, notify = notification_controllers.read_group_notifications(request,
                                                                          member_email=query.get(
                                                                              'owner_email', None),
                                                                          group_id=query.get(
                                                                              'group_id', None),
                                                                          notification_id=notification_id
                                                                          )
    elif topic == 'all':
        total_owner, notify = notification_controllers.read_owner_notifications(request,
                                                                                owner_email=query.get(
                                                                                    'owner_email', None),
                                                                                notification_id=notification_id
                                                                                )
        total_group, notify = notification_controllers.read_group_notifications(request,
                                                                                member_email=query.get(
                                                                                    'owner_email', None),
                                                                                group_id=query.get(
                                                                                    'group_id', None),
                                                                                notification_id=notification_id
                                                                                )
        total = total_owner + total_group
    else:
        raise BadRequest(
            request, error_code=ErrorCodes.Validation.BadRequest, args=get_request_user(request))

    return {
        'message': "{total} notifications marked as read".format(total=total)
    }


@is_authenticated(redirect_url='/')
def notification_count_per_group(request):
    """
    Handles any request sent to following urls:
            /notification/group-count

    Parameters
    ----------
    request - HTTP Request

    Returns
    -------
    response : JSON Response

    """

    query = request.GET
    member_email = query.get('member_email', None)
    is_read = query.get('is_read', None)

    if is_read == 'true':
        is_read = True
    elif is_read == 'false':
        is_read = False
    else:
        is_read = None

    # Validate get notifications API request
    user_role = authorization.user_role(request)
    if user_role == authorization.UserRole.LOGGED_IN:
        if get_request_user(request) != member_email:
            raise BadRequest(
                request, error_code=ErrorCodes.Validation.NotAllowedNotificationAccess, args=get_request_user(request))

    total, count_per_group = notification_controllers.get_notification_count_per_group(request,
                                                                                       member_email=member_email,
                                                                                       is_read=is_read)

    return HttpResponse(json.dumps({
        'total': total,
        'groups': [{'group': utils.serializer(g[0]), 'count': int(g[1])} for g in count_per_group]
    }),
        content_type="application/json",
        status=200)


@is_authenticated(redirect_url="/")
def notifications_send_email_api(request):
    """
    Handles any request sent to following urls:
            /ajax/notification/email-status

    Parameters
    ----------
    request - HTTP Request

    Returns
    -------
    response : JSON Response

    """
    owner_email = request.GET.get("owner_email", QueryDict(
        request.body).get("owner_email", None))
    if request.META.get('HTTP_ACCEPT', None) == 'application/json':
        if request.method == "GET":
            return HttpResponse(json.dumps(_get_notifications_send_email_status(request, owner_email=owner_email, query=request.GET)), content_type="application/json")
        elif request.method == "PUT":
            return HttpResponse(json.dumps(_update_notifications_send_email_status(
                request,
                owner_email=owner_email,
                query=QueryDict(request.body))
            ),
                content_type="application/json",
                status=200)
        else:
            # Handle other type of request methods like OPTIONS etc.
            raise MethodNotAllowed(request)
    else:
        raise BadRequest(request)


def _get_notifications_send_email_status(request, owner_email, query):
    """

    Query Parameters
    ----------
    owner_email : string
            Email of the Owner of the notification.

    Parameters
    ----------
    query : dict
            Dictionary of query parameters.
    request : object
            HTTP GET Request.

    Returns
    -------
    receive_notification_email : Status on whether to send notification email

    Raises
    ------

    Notes
    ------

    """
    user = utils.serializer(
        user_controllers.get_user(request, email=owner_email))
    return {
        "receive_notification_email": user.get("receive_notification_email", False)
    }


def _update_notifications_send_email_status(request, owner_email, query):
    """

    Query Parameters
    ----------
    owner_email : string
            Email of the Owner of the notification.

    Parameters
    ----------
    query : dict
            Dictionary of query parameters.
    request : object
            HTTP GET Request.

    Returns
    -------
    receive_notification_email : Updated status on whether to send notification email

    Raises
    ------

    Notes
    ------

    """
    user = utils.serializer(
        user_controllers.get_user(request, email=owner_email))
    receive_notification_email = not user.get(
        "receive_notification_email", False)
    updated_user = utils.serializer(user_controllers.update_user(
        request, user_id=user["id"], receive_notification_email=receive_notification_email))

    return {
        "receive_notification_email": updated_user.get("receive_notification_email", False)
    }
