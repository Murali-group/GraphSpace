import bcrypt
import applications.users.dal as db
from graphspace.utils import generate_uid


def authenticate(request, username=None, password=None):
	# check the username/password and return a User
	user = db.get_user(request.db_session, username)

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


def get_user(request, email):
	return db.get_user(request.db_session, email) if email is not None else None


def register(request, username=None, password=None):
	if db.get_user(request.db_session, username):
		raise Exception("Email already exists!")

	try:
		return add_user(request.db_session, email=username, password=bcrypt.hashpw(password, bcrypt.gensalt()))
	except Exception as e:
		raise e


def add_user(request, email="public_user_%s@graphspace.com" % generate_uid(size=10), password="graphspace_public_user", is_admin=0):
	"""
	Add a new user. If email and password is not passed, it will create a user with default values.
	By default a user has no admin access.

	:param db_session: Database session.
	:param email: User ID of the user. Default value is dynamically generated user id.
	:param password: Password of the user. Default value is "public".
	:param admin: 1 if user has admin access else 0. Default value is 0.
	:return: User
	"""
	return db.add_user(request.db_session, email=email, password=bcrypt.hashpw(password, bcrypt.gensalt()), is_admin=is_admin)


def is_member_of_group(request, username, group_id):
	is_member = False
	if username is not None and group_id is not None:
		user = db.get_user(request.db_session, username)
		if db.get_group_to_user(request.db_session, group_id, user.id) is not None:
			is_member = True
	return is_member