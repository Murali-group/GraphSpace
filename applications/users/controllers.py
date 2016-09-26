import bcrypt
import applications.users.dal as users


def authenticate(request, username=None, password=None):
	# check the username/password and return a User
	user = users.get_user(request.db_session, username)

	if user:
		hashed_pw = user.password

		#check password. if the password matches, return a
		#User object with associated information
		if bcrypt.hashpw(password, hashed_pw) == hashed_pw:
			return {
				'user_id': user.email,
				'password': user.password,
				'admin': user.is_admin
			}
	else:
		return None


def register(request, username=None, password=None):
	if users.get_user(request.db_session, username):
		raise Exception("Email already exists!")

	try:
		return users.add_user(request.db_session, email=username, password=bcrypt.hashpw(password, bcrypt.gensalt()))
	except Exception as e:
		raise e


