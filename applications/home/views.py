from django.conf import settings
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

@login_required(login_url="login/")
def index(request):
	"""
        Render the main page

        :param request: HTTP GET Request
    """
	context = {
		'uid': None,
		'url': settings.URL_PATH
	}

	return render(request, 'home/index.html', context)
