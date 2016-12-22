import json
from applications.users.forms import RegisterForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import applications.users.controllers as users
from django.template import RequestContext
from graphspace.utils import *


def index(request):
	"""
		Render the main page.

		:param request: HTTP Request
	"""

	context = RequestContext(request) # Checkout base.py file to see what context processors are being applied here.
	print(context)
	if 'GET' == request.method:
		# Handle GET request to index page.
		return render(request, 'home/index.html', context)
	else:
		# Handle other type of request methods like POST, PUT, UPDATE.
		raise Exception


def login(request):
	"""
		Handles login (POST) request.

		:param request: HTTP Request
	"""
	if 'POST' == request.method:
		try:
			user = users.authenticate_user(request, username=request.POST['user_id'], password=request.POST['pw'])

			if user is not None:
				request.session['uid'] = user['user_id']
				request.session['admin'] = user['admin']
				return HttpResponse(json.dumps(json_success_response(200, message='%s, Welcome to GraphSpace!' % user['user_id'])), content_type="application/json")
			else:
				return HttpResponse(json.dumps(json_error_response(400, "User/Password not recognized!")), content_type="application/json")
		except Exception as e:
			return HttpResponse(json.dumps(json_error_response(400, str(e))), content_type="application/json")
	else:
		return HttpResponse(json.dumps(json_error_response(400)), content_type="application/json")


def register(request):
	"""
		Register a new user.

		:param request: HTTP POST Request containing:

		{"user_id": <user_id>, "password": <password>}
	"""

	if 'POST' == request.method and 'user_id' in request.POST and 'password' in request.POST:
		# RegisterForm is bound to POST data
		register_form = RegisterForm(request.POST)
		if register_form.is_valid():
			try:
				user = users.register(request, username=register_form.cleaned_data['user_id'], password=register_form.cleaned_data['password'])
				return HttpResponse(json.dumps(json_success_response(200, message='Registered!')), content_type="application/json")
			except Exception as e:
				return HttpResponse(json.dumps(json_error_response(400, str(e))), content_type="application/json")
	else:
		return HttpResponse(json.dumps(json_error_response(400)), content_type="application/json")


def logout(request):
	"""
		Log the user out and display logout page.

		:param request: HTTP GET Request

	"""
	try:
		del request.session['uid']  # Deletes the "Uid" key from the session currently being tracked by Django.
	except KeyError:
		pass  # TODO: should something be done here?

	return HttpResponseRedirect('/')  # redirect to the main page after logout.
