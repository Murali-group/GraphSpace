import json

import applications.uniprot.controllers as uniprot
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from graphspace import utils
import graphspace.authorization as authorization
from graphspace.wrappers import is_authenticated
from graphspace.exceptions import MethodNotAllowed, BadRequest, ErrorCodes
from graphspace.utils import get_request_user


'''
Alias APIs
'''

@csrf_exempt
def uniprot_alias_ajax_api(request):
	"""
	Handles any request sent to following urls:
		/javascript/alias

	Parameters
	----------
	request - HTTP Request

	Returns
	-------
	response : JSON Response

	"""
	return _uniprot_alias_api(request)


def _uniprot_alias_api(request):
	"""
	Handles any request (GET) sent to /alias

	Parameters
	----------
	request - HTTP Request

	Returns
	-------

	"""
	if 'application/json' in request.META.get('HTTP_ACCEPT', None):
		if request.method == "GET":
			return HttpResponse(json.dumps(_get_uniprot_aliases(request, query=request.GET)), content_type="application/json")
		else:
			raise MethodNotAllowed(request)  # Handle other type of request methods like OPTIONS etc.
	else:
		raise BadRequest(request)


def _get_uniprot_aliases(request, query={}):
	"""

	Query Parameters
	----------
	limit : integer
		Number of entities to return. Default value is 20.
	offset : integer
		Offset the list of returned entities by this number. Default value is 0.
	q : string
		Search for aliases with given name. In order to search for aliases with given name as a substring, wrap the name with percentage symbol. For example, %xyz% will search for all aliases with xyz in their name.

	Parameters
	----------
	query : dict
		Dictionary of query parameters.
	request : object
		HTTP GET Request.

	Returns
	-------
	total : integer
		Number of aliases matching the request.
	uniprot_aliases : List of uniprot_aliases.
		List of uniprot_alias Objects with given limit and offset.

	Raises
	------

	Notes
	------

	"""

	total, uniprot_aliases = uniprot.search_uniprot_aliases(request,
										accession_number=query.get('q', None),
										alias_name=query.get('q', None),
										limit=query.get('limit', 20),
										offset=query.get('offset', 0))

	return {
		'total': total,
		'uniprot_aliases': [utils.serializer(uniprot_alias) for uniprot_alias in uniprot_aliases]
	}