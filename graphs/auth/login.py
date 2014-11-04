from django.contrib.auth import authenticate
from graphs.forms import LoginForm, RegisterForm


def login(request):
	'''
	Handles the login request from the webpage.

	django.contrib.auth.authenticate uses authenticate() function defined in
	graph.auth.AuthBackend
	'''
	#context of the view to be passed in for rendering
	context = {}
	message = ''
	login_form = LoginForm();
	register_form = RegisterForm();

	if request.method == 'POST':
		user = authenticate(username=request.POST['user_id'], password=request.POST['pw'])
		login_form = LoginForm(request.POST)
		if user is not None:
			message = '%s, Welcome to GraphSpace!' % user.user_id
			request.session['uid'] = user.user_id
			request.session['admin'] = user.admin
			context = {'message': message, 'login_form': login_form, 'user': user, 'uid': user.user_id, 'admin': user.admin, "Error": None}
			return context
		else:
			login_form = LoginForm()
			context['login_form'] = login_form
			context['register_form'] = register_form
			context['Error'] = "User/Password not recognized!"
			message = 'Information you have given does not match our records. Please try again.'
			context['message'] = message
			return context
	# when a user is already logged in or not logged in at all.
	else:
		# this replacement does not handle logout properly.
		########### Possible replacement #############
        # the user did not enter any information into the login form. 
        # in this case, there may be already be a logged-in user. 
        
		# if request.session['uid'] is not None:
		# 	# there is a currently logged-in user.
		# 	context['uid'] = request.session['uid']
		# 	message = '%s, Welcome to Graphspace!' % request.session['uid']
		# else:
		# 	# there is no one logged in.
		# 	login_form = LoginForm()
		# 	request.session['uid'] = None
		# 	message = 'Welcome to GraphSpace!'
		# 	context['login_form'] = login_form
		########### END possible replacement ############

		############ Original code commented for possible revert  ##########
		if 'uid' in request.session:
            #there is a currently logged-in user.
			uid = request.session['uid']
		else:
			#there is no one logged in.
			uid = None
		
		if uid is not None:
			context['uid'] = request.session['uid']
			context['admin'] = request.session['admin']
			context['Error'] = None
			message = 'Welcome to GraphSpace, %s!' % request.session['uid']
			context["message"] = message
			return context
		else:
			request.session['uid'] = None
 			context['message'] = 'Welcome to GraphSpace!'
 			context['login_form'] = login_form
 			context['register_form'] = RegisterForm()
 			context["Error"] = None
 			return context
		############ END original code ############

	# context['message'] = message
	# return context
