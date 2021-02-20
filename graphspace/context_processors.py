from django.conf import settings
from applications.users.forms import LoginForm, RegisterForm


def auth(request):
	return {
		'uid': request.session['uid'] if 'uid' in request.session else None,
		'admin': request.session['admin'] if 'admin' in request.session else None,
	}


def maintenance(request):
	return {
		'is_maintenance_scheduled': settings.IS_MAINTENANCE_SCHEDULED,
		'maintenance_start_datetime': settings.MAINTENANCE_START_DATETIME,
		'maintenance_end_datetime': settings.MAINTENANCE_END_DATETIME,
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
