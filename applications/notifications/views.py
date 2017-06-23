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
from graphspace.exceptions import MethodNotAllowed, BadRequest, ErrorCodes
from graphspace.utils import get_request_user


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
                    Rendered graphs list page in HTML.

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
    type = query.get('type', None)
    owner_email = query.get('owner_email', None)
    # Validate get notifications API request
    user_role = authorization.user_role(request)
    if user_role == authorization.UserRole.LOGGED_IN:
        if get_request_user(request) != owner_email:
            raise BadRequest(request, error_code=ErrorCodes.Validation.NotAllowedNotificationAccess,
                             args=get_request_user(request))
    if type == 'owner':
        message, notify = notification_controllers.read_owner_notifications(request,
                                                                            owner_email=owner_email,
                                                                            notification_id=notification_id
                                                                            )
        notify = utils.serializer(notify)
    else:
        raise BadRequest(
            request, error_code=ErrorCodes.Validation.BadRequest, args=get_request_user(request))

    url = '/{resource}/{resource_id}'.format(**notify)
    resource = notify.get('resource', None)
    resource_id = notify.get('resource_id', None)
    if resource == 'layout':
        return_value = utils.serializer(
            graph_controllers.get_layout_by_id(request, resource_id))
        if return_value is not None:
            url = '/graphs/{graph_id}?user_layout={id}'.format(**return_value)
    elif resource == 'graph':
        return_value = graph_controllers.get_graph_by_id(request, resource_id)
    elif resource == 'group':
        return_value = user_controllers.get_group_by_id(request, resource_id)
    if return_value is None:
        url = '/notifications'
    print url
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
    type : string
            Type of the notification [owner, group, watching].

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

    type = query.get('type', None)
    is_read = query.get('is_read', None)

    if is_read == 'true':
        is_read = True
    elif is_read == 'false':
        is_read = False
    else:
        is_read = None

    if type == 'owner':
        total, notifications = notification_controllers.search_owner_notifications(request,
                                                                                   owner_email=query.get(
                                                                                       'owner_email', None),
                                                                                   is_read=is_read,
                                                                                   limit=query.get(
                                                                                       'limit', 20),
                                                                                   offset=query.get('offset', 0))
    else:
        raise BadRequest(
            request, error_code=ErrorCodes.Validation.BadRequest, args=get_request_user(request))

    return {
        'total': total,
        'notifications': [utils.serializer(notification) for notification in notifications]
    }


def _update_notifications_read(request, notification_id=None, query={}):
    """

    Query Parameters
    ----------
    owner_email : string
            Email of the Owner of the notification.
    type : string
            Type of the notification [owner, group, watching].

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

    type = query.get('type', None)

    if type == 'owner':
        message, notify = notification_controllers.read_owner_notifications(request,
                                                                            owner_email=query.get(
                                                                                'owner_email', None),
                                                                            notification_id=notification_id
                                                                            )
    else:
        raise BadRequest(
            request, error_code=ErrorCodes.Validation.BadRequest, args=get_request_user(request))

    return {
        'message': message
    }
