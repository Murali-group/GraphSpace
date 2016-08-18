from graphs_old.auth import AuthBackend
from graphs_old.forms import LoginForm, RegisterForm
from graphs_old.util import db
from django.conf import settings

def login(request):
	'''
		Handles the login request from the webpage.
	'''
	#context of the view to be passed in for rendering
	context = {}
	message = ''
	login_form = LoginForm();
	register_form = RegisterForm();
	URL_PATH = settings.URL_PATH

	if request.method == 'POST':

		user = AuthBackend.authenticate(username=request.POST['user_id'], password=request.POST['pw'])
		login_form = LoginForm(request.POST)
		if user is not None:
			message = '%s, Welcome to GraphSpace!' % user['user_id']
			request.session['uid'] = user['user_id']
			request.session['admin'] = user['admin']
			context = {'login_form': login_form, 'user': user, 'uid': user['user_id'], 'admin': user['admin'], "Error": None, "url": URL_PATH}
			return context
		else:
			login_form = LoginForm()
			context['login_form'] = login_form
			context['register_form'] = register_form
			context['Error'] = "User/Password not recognized!"
			message = 'Information you have given does not match our records. Please try again.'
			context['url'] = URL_PATH
			return context
	# when a user is already logged in or not logged in at all.
	else:
        # the user did not enter any information into the login form. 
        # in this case, there may be already be a logged-in user. 
  		if 'uid' in request.session:
            #there is a currently logged-in user.
			uid = request.session['uid']
		else:
			#there is no one logged in.
			uid = None
			context['url'] = URL_PATH
			context['Error'] = "Not logged in!"

		if uid is not None:
			context['uid'] = request.session['uid']
			context['admin'] = request.session['admin']
			context['Error'] = None
			message = 'Welcome to GraphSpace, %s!' % request.session['uid']
			context['url'] = URL_PATH
			return context
		else:
			request.session['uid'] = None
 			context['login_form'] = login_form
 			context['register_form'] = RegisterForm()
			context['url'] = URL_PATH
 			context["Error"] = None
 			return context
