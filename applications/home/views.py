import json
from applications.users.forms import RegisterForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import applications.users.controllers as users
from django.template import RequestContext
from graphspace.utils import *
from graphspace.exceptions import *


def home_page(request):
	"""
	Wrapper view function for the following pages:
		/
		/index

	Parameters
	----------
	request : HTTP Request

	Returns
	-------
	response : HTML Page Response
		Rendered home page in HTML.

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

	Notes
	------

	"""
	context = RequestContext(request)  # Checkout base.py file to see what context processors are being applied here.

	if 'GET' == request.method:
		return render(request, 'home/index.html', context.flatten())  # Handle GET request to index page.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


def features_page(request):
	"""
	Wrapper view function for the following pages:
		/features

	Parameters
	----------
	request : HTTP Request

	Returns
	-------
	response : HTML Page Response
		Rendered features page in HTML.

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

	Notes
	------

	"""
	context = RequestContext(request)  # Checkout base.py file to see what context processors are being applied here.

	if 'GET' == request.method:
		return render(request, 'features/index.html', context.flatten())  # Handle GET request to index page.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


def help_page(request):
	"""
	Wrapper view function for the following pages:
		/help

	Parameters
	----------
	request : HTTP Request

	Returns
	-------
	response : HTML Page Response
		Rendered help page in HTML.

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

	Notes
	------

	"""
	context = RequestContext(request)  # Checkout base.py file to see what context processors are being applied here.

	if 'GET' == request.method:
		return render(request, 'help/index.html', context.flatten())  # Handle GET request to index page.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


def about_us_page(request):
	"""
	Wrapper view function for the following pages:
		/about_us

	Parameters
	----------
	request : HTTP Request

	Returns
	-------
	response : HTML Page Response
		Rendered about us page in HTML.

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

	Notes
	------

	"""
	context = RequestContext(request)  # Checkout base.py file to see what context processors are being applied here.

	if 'GET' == request.method:
		return render(request, 'about_us/index.html', context.flatten())  # Handle GET request to index page.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like POST, PUT, UPDATE.


def forgot_password_page(request):
	"""
	Wrapper view function for the following pages:
		/forgot_password

	Parameters
	----------
	request : HTTP Request

	Returns
	-------
	response : HTML Page Response
		Rendered forgot password page in HTML.

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET i.e., POST, PUT or UPDATE.

	Notes
	------

	"""
	context = RequestContext(request)  # Checkout base.py file to see what context processors are being applied here.

	if 'GET' == request.method:
		return render(request, 'forgot_password/index.html', context.flatten())  # Handle GET request to forgot password page.
	elif 'POST' == request.method:
		email = request.POST.get('forgot_email', None)

		if users.get_user(request, email) is not None:
			password_reset_code = users.add_user_to_password_reset(request, email)
			users.send_password_reset_email(request, password_reset_code)
			context["success_message"] = "You will receive an email with a link to update the password!"
		else:
			context["error_message"] = "No account is associated with that email address"
		return render(request, 'forgot_password/index.html', context.flatten())  # Handle POST request to forgot password page.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like PUT, UPDATE.


def reset_password_page(request):
	"""
	Wrapper view function for the following pages:
		/reset_password

	Parameters
	----------
	request : HTTP Request

	Returns
	-------
	response : HTML Page Response
		Rendered reset password page in HTML.

	Raises
	------
	MethodNotAllowed: If a user tries to send requests other than GET and POST i.e. PUT or UPDATE.

	Notes
	------

	"""
	context = RequestContext(request)  # Checkout base.py file to see what context processors are being applied here.

	if 'GET' == request.method:
		password_reset_code = users.get_password_reset_by_code(request, request.GET.get('code', None))
		if password_reset_code is None:
			context['error_message'] = "This password reset link is outdated. Please try resetting your password again."
		else:
			context['email'] = password_reset_code.email
		return render(request, 'reset_password/index.html', context.flatten())  # Handle GET request to index page.
	elif 'POST' == request.method:
		password_reset_code = users.get_password_reset_by_code(request, request.GET.get('code', None))

		if password_reset_code is not None:
			users.update_user(request, password_reset_code.user.id, password=request.POST['password'])
			context["success_message"] = "Password updated for " + request.POST['reset_email']
			context['email'] = password_reset_code.email
			users.delete_password_reset_code(request, password_reset_code.id)
		else:
			context['error_message'] = "This password reset link is outdated. Please try resetting your password again."

		return render(request, 'reset_password/index.html', context.flatten())  # Handle POST request to forgot password page.
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like PUT, UPDATE.


def login(request):
	"""
		Handles login (POST) request.

		:param request: HTTP Request
	"""
	if 'POST' == request.method:
		request_body = json.loads(request.body)
		user = users.authenticate_user(request, username=request_body['user_id'], password=request_body['pw'])

		if user is not None:
			request.session['uid'] = user['user_id']
			request.session['admin'] = user['admin']
			return HttpResponse(
				json.dumps(json_success_response(200, message='%s, Welcome to GraphSpace!' % user['user_id'])),
				content_type="application/json")
		else:
			raise ValidationError(request, ErrorCodes.Validation.UserPasswordMisMatch)
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like GET, PUT, UPDATE.


def register(request):
	"""
		Register a new user.

		:param request: HTTP POST Request containing:

		{"user_id": <user_id>, "password": <password>}
	"""

	if 'POST' == request.method:
		request_body = json.loads(request.body)
		if 'user_id' in request_body and 'password' in request_body:
			# RegisterForm is bound to POST data
			register_form = RegisterForm(request_body)
			if register_form.is_valid():
				user = users.register(request, username=register_form.cleaned_data['user_id'],
				                      password=register_form.cleaned_data['password'])
				if user is not None:
					request.session['uid'] = user.email
					request.session['admin'] = user.is_admin

			return HttpResponse(json.dumps(json_success_response(200, message='Registered!')),
			                    content_type="application/json")
		else:
			raise BadRequest(request)
	else:
		raise MethodNotAllowed(request)  # Handle other type of request methods like GET, PUT, UPDATE.


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


def images(request, query):
	"""
		Redirect request to /images to /static/images

		The problem is that the link to images folder was hardcoded previously in the popups.

		:param request: HTTP GET Request

	"""
	return redirect('/static' + request.path)