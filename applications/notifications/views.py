import json

#import applications.graphs.controllers as graphs
#import applications.users.controllers as users
import graphspace.authorization as authorization
import graphspace.utils as utils
from django.conf import settings
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from graphspace.exceptions import MethodNotAllowed, BadRequest, ErrorCodes
from graphspace.utils import get_request_user
from graphspace.wrappers import is_authenticated


def notifications_page(request):
	"""
		Wrapper view function for the following pages:
		/graphs/

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
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.

