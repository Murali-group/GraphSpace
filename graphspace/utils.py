import json
import string
import base64

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


def serializer(obj, summary=False):
	return obj.serialize(summary=summary) if obj is not None else None


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

