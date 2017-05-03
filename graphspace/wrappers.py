from django.shortcuts import redirect
import base64
import applications.users as users
from graphspace.exceptions import UserNotAuthenticated


def with_session(inner):
	def inner_decorator(db_session, *args, **kwargs):
		# TODO: Add error logs and access logs and handle exceptions.
		try:
			result = inner(db_session, *args, **kwargs)
			db_session.flush()
			return result
		except:
			db_session.rollback()
			raise

	return inner_decorator


def atomic_transaction(inner):
	def inner_decorator(request, *args, **kwargs):
		try:
			result = inner(request, *args, **kwargs)
			request.db_session.flush()
			return result
		except:
			request.db_session.rollback()
			raise

	return inner_decorator


def login_required(redirect_url='/'):
	def wrapper(inner):
		def inner_decorator(request, *args, **kwargs):
			try:
				if request.session['uid'] is not None:
					return inner(request, *args, **kwargs)
				else:
					return redirect(redirect_url)
			except:
				raise
		return inner_decorator
	return wrapper


def is_user_logged_in(request):
	return request.session['uid'] is not None


def has_basic_authentication(request):
	if 'HTTP_AUTHORIZATION' in request.META:
		auth = request.META['HTTP_AUTHORIZATION'].split()
		if len(auth) == 2:
			if auth[0].lower() == "basic":
				uname, passwd = base64.b64decode(auth[1]).split(':')
				user = users.controllers.authenticate_user(request, username=uname, password=passwd)
				return user is not None
	return False


def is_authenticated(redirect_url=None):
	def wrapper(inner):
		def inner_decorator(request, *args, **kwargs):
			try:
				if is_user_logged_in(request) or has_basic_authentication(request):
					return inner(request, *args, **kwargs)
				elif redirect_url is not None:
					return redirect(redirect_url)
				else:
					raise UserNotAuthenticated(request)
			except:
				raise
		return inner_decorator
	return wrapper

