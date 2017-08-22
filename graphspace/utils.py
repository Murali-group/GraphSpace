import json
import string
import base64
import re

from django.utils.crypto import random


def generate_uid(size=20, chars=string.ascii_uppercase + string.digits):
	"""
		Generates an unique alphanumeric ID of specific size.

		:param size: Size of random string
		:param chars: Subset of characters to generate random string of
		:return string: Random string that adhere to the parameter properties
	"""
	return ''.join(random.choice(chars) for _ in range(size))


def get_request_user(request):
	if 'HTTP_AUTHORIZATION' in request.META:
		auth = request.META['HTTP_AUTHORIZATION'].split()
		if len(auth) == 2:
			if auth[0].lower() == "basic":
				uname, passwd = base64.b64decode(auth[1]).split(':')
				return uname
	return request.session['uid'] if 'uid' in request.session else None


def serializer(obj):
	return obj.serialize() if obj is not None else None


def json_success_response(status_code=200, message=""):
	return {
		"StatusCode": status_code,
		"Message": message
	}


def json_error_response(status_code=500, error=""):
	return {
		"StatusCode": status_code,
		"Error": error
	}


def cytoscapePresetLayout(csWebJson):
	"""
		Converts CytoscapeWeb preset layouts to be
		the standards of CytoscapeJS JSON. See http://js.cytoscape.org/#layouts/preset
		for more details.

		:param csWebJson: A CytoscapeWeb compatible layout json containing coordinates of the nodes
		:return csJson: A CytoscapeJS compatible layout json containing coordinates of the nodes
	"""
	csJson = {}

	# csWebJSON format: [{x: x coordinate of node, y: y coordinate of node, id: id of node},...]
	# csJson format: [id of node: {x: x coordinate of node, y: y coordinate of node},...]

	for node_position in csWebJson:

		csJson[str(node_position['id'])] = {
			'x': node_position['x'],
			'y': node_position['y']
		};

		if 'background_color' in node_position:
			csJson[str(node_position['id'])]["background_color"] = node_position['background_color']

		if 'shape' in node_position:
			csJson[str(node_position['id'])]['shape'] = node_position['shape']

	return json.dumps(csJson)


def websocket_group_name(name):
    """ 
    	Django-channels only accepts alphanumerics, hyphen and period; 
    	Remove all other symbols 
    """
    return re.sub('[^a-zA-Z0-9\n\.]', '-', name)


def group_notification_bulk_serializer(notify):
	"""
		Serialize row to dict format
	"""
	return {
        'id': notify[0],
        'message': (notify[1] + ' ' + notify[4] + ' ' + settings.NOTIFICATION_MESSAGE['group'][notify[3]]['bulk'] + '.') if notify[2] else notify[1],
        'is_bulk': notify[2],
        'type': notify[3],
        'resource': notify[4],
        'owner_email': notify[5],
        'member_email': notify[6],
        'group_id': notify[7],
        'created_at': notify[8].isoformat(),
        'first_created_at': notify[9].isoformat(),
        'is_read': True if notify[10] == 1 else False
    }


def owner_notification_bulk_serializer(notify):
	"""
		Serialize row to dict format
	"""
	return {
        'id': notify[0],
        'message': (notify[1] + ' ' + notify[4] + ' ' + settings.NOTIFICATION_MESSAGE['owner'][notify[3]]['bulk'] + '.') if notify[2] else notify[1],
        'is_bulk': notify[2],
        'type': notify[3],
        'resource': notify[4],
        'owner_email': notify[5],
        'created_at': notify[6].isoformat(),
        'first_created_at': notify[7].isoformat(),
        'is_read': True if notify[8] == 1 else False
    }
