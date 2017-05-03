from django.conf import settings
from applications.users.forms import LoginForm, RegisterForm


def auth(request):
	return {
		'uid': request.session['uid'] if 'uid' in request.session else None,
		'admin': request.session['admin'] if 'admin' in request.session else None,
	}


def static_urls(request):
	return {
		'url': settings.URL_PATH
	}


def login_forms(request):
	return {
		'url': settings.URL_PATH,
		'login_form': LoginForm(),
		'register_form': RegisterForm()
	}
