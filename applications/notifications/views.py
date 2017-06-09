import json

import applications.notifications.controllers as notification_controllers
import graphspace.authorization as authorization
import graphspace.utils as utils
from django.conf import settings
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
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
            /javascript/notifications
            /javascript/notifications/<group_id>

    Parameters
    ----------
    request - HTTP Request

    Returns
    -------
    response : JSON Response

    """
    return _notifications_api(request, notification_id=notification_id)


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
        elif request.method == "PUT" and notification_id is not None:
            return HttpResponse(json.dumps(_update_notification(request, notification_id, notification=QueryDict(request.body))),
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
    status: string
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

    total, notifications = notification_controllers.search_notifications(request,
                                                                         owner_email=query.get(
                                                                             'owner_email', None),
                                                                         status=query.get(
                                                                             'status', None),
                                                                         type=query.get(
                                                                             'type', None),
                                                                         limit=query.get(
                                                                             'limit', 20),
                                                                         offset=query.get('offset', 0))

    return {
        'total': total,
        'notifications': [utils.serializer(notification) for notification in notifications]
    }
