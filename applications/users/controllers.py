import bcrypt

from django.conf import settings
from django.core.mail import send_mail

import applications.graphs as graphs
import applications.users.dal as db
from graphspace.exceptions import BadRequest, ErrorCodes
from graphspace.utils import generate_uid


from mailmanclient import Client

client = Client('http://localhost:8001/3.1', 'restadmin', 'restpass')

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def authenticate_user(request, username=None, password=None):

	# check the username/password and return a User
	user = db.get_user(request.db_session, username)

	if user:
		hashed_pw = user.password

		#check password. if the password matches, return a
		#User object with associated information
		if bcrypt.hashpw(password, hashed_pw) == hashed_pw:
			return {
				'id': user.id,
				'user_id': user.email,
				'password': user.password,
				'admin': user.is_admin,
				'user_account_status':user.user_account_status,
				'email_list_announcement': user.email_list_announcement,
				'email_list_user': user.email_list_user
			}
	else:
		return None


def update_user(request, user_id, email=None, password=None, is_admin=None, user_account_status=None, email_list_announcement=None, email_list_user=None):
	user = {}
	if email is not None:
		user['email'] = email
	if password is not None:
		user['password'] = bcrypt.hashpw(password, bcrypt.gensalt())
	if is_admin is not None:
		user['is_admin'] = is_admin
	if user_account_status is not None:
		user['user_account_status'] = user_account_status
	if email_list_announcement is not None:
		user['email_list_announcement'] = email_list_announcement
		if email_list_announcement == '1':
			client_list_announcement = client.get_list(settings.ANNOUNCEMENTS_LIST)
			client_list_announcement.subscribe(email, pre_verified=True, pre_confirmed=True)
	if email_list_user is not None:
		user['email_list_user'] = email_list_user
		if email_list_user == '1':
			client_list_user = client.get_list(settings.USERS_LIST)
			client_list_user.subscribe(email, pre_verified=True, pre_confirmed=True)
	return db.update_user(request.db_session, id=user_id, updated_user=user)


def is_user_authorized_to_share_with_group(request, username, group_id):
	is_authorized = False

	group = db.get_group(request.db_session, group_id)

	if group is not None:  # Graph exists
		if group.owner_email == username:
			is_authorized = True
		elif is_member_of_group(request, username, group_id):  # graph is public
			is_authorized = True

	return is_authorized


def is_user_authorized_to_delete_group(request, username, group_id):
	is_authorized = False

	group = db.get_group(request.db_session, group_id)

	if group is not None:  # Graph exists
		if group.owner_email == username:
			is_authorized = True

	return is_authorized


def is_user_authorized_to_view_group(request, username, group_id):
	is_authorized = False

	group = db.get_group(request.db_session, group_id)

	if group is not None:  # Graph exists
		if group.owner_email == username:
			is_authorized = True
		elif is_member_of_group(request, username, group_id):  # graph is public
			is_authorized = True

	return is_authorized


def is_user_authorized_to_update_group(request, username, group_id):
	is_authorized = False

	group = db.get_group(request.db_session, group_id)

	if group is not None:  # Graph exists
		if group.owner_email == username:
			is_authorized = True

	return is_authorized


def get_user(request, email):
	return db.get_user(request.db_session, email) if email is not None else None


def search_users(request, email=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'email':
		sort_attr = db.User.email
	elif sort == 'updated_at':
		sort_attr = db.User.updated_at
	else:
		sort_attr = db.User.email

	if order == 'desc':
		orber_by = db.desc(sort_attr)
	else:
		orber_by = db.asc(sort_attr)

	total, users = db.find_users(request.db_session,
						email=email,
						limit=limit,
						offset=offset,
						order_by=orber_by)

	return total, users


def register(request, username=None, password=None, user_account_status=None, email_confirmation_code=None, email_list_announcement=None, email_list_user=None):
	if db.get_user(request.db_session, username):
		raise BadRequest(request, error_code=ErrorCodes.Validation.UserAlreadyExists, args=username)

	return add_user(request, email=username, password=password, user_account_status=user_account_status,
					email_confirmation_code=email_confirmation_code, email_list_announcement=email_list_announcement,
					email_list_user=email_list_user)


def add_user(request, email=None, password="graphspace_public_user", is_admin=0, user_account_status=None, email_confirmation_code=None, email_list_announcement=None, email_list_user=None):
	"""
	Add a new user. If email and password is not passed, it will create a user with default values.
	By default a user has no admin access.

	:param db_session: Database session.
	:param email: User ID of the user. Default value is dynamically generated user id.
	:param password: Password of the user. Default value is "public".
	:param admin: 1 if user has admin access else 0. Default value is 0.
	:return: User
	"""
	email = "public_user_%s@graphspace.com" % generate_uid(size=10) if email is None else email

	return db.add_user(request.db_session, email=email, password=bcrypt.hashpw(password, bcrypt.gensalt()), is_admin=is_admin,
					   user_account_status=user_account_status, email_confirmation_code=email_confirmation_code, email_list_announcement=email_list_announcement,
					email_list_user=email_list_user)


def is_member_of_group(request, username, group_id):
	is_member = False
	if username is not None and group_id is not None:
		user = db.get_user(request.db_session, username)
		if db.get_group_to_user(request.db_session, group_id, user.id) is not None:
			is_member = True
	return is_member


def add_group(request, name, owner_email, description):
	if name is None or owner_email is None:
		raise Exception("Required Parameter is missing!")
	group = db.add_group(request.db_session, name=name, owner_email=owner_email, description=description)
	add_group_member(request, group_id=group.id, member_email=owner_email)
	return group


def get_groups_by_member_id(request, member_id):
	"""
	Returns all groups where user with given user_id is a member.
	:param request: HTTP Request
	:param member_id: ID of a user who is a member of one or many groups.
	:return: list of Groups
	"""
	return db.get_groups_by_member_id(request.db_session, member_id=member_id)


def get_groups_by_owner_id(request, owner_id):
	"""
	Returns all groups where user with give email is a owner.
	:param request: HTTP Request
	:param owner_id: email of a user who owns one or many groups.
	:return: list of Groups
	"""
	return db.get_groups_by_owner_id(request.db_session, owner_id=owner_id)


def search_groups(request, owner_email=None, member_email=None, name=None, description=None, graph_ids=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'name':
		sort_attr = db.Group.name
	elif sort == 'updated_at':
		sort_attr = db.Group.updated_at
	elif sort == 'owner_email':
		sort_attr = db.Group.owner_email
	else:
		sort_attr = db.Group.name

	if order == 'desc':
		orber_by = db.desc(sort_attr)
	else:
		orber_by = db.asc(sort_attr)

	total, groups = db.find_groups(request.db_session,
						owner_email=owner_email,
						member_email=member_email,
						name=name,
						description=description,
						graph_ids=graph_ids,
						limit=limit,
						offset=offset,
						order_by=orber_by)

	return total, groups


def get_group_by_id(request, group_id):
	return db.get_group(request.db_session, id=group_id)


def delete_group_by_id(request, group_id):
	db.delete_group(request.db_session, id=group_id)
	return


def update_group(request, group_id, name, description, owner_email):
	group = {}
	if name is not None:
		group['name'] = name
	if description is not None:
		group['description'] = description
	if owner_email is not None:
		group['owner_email'] = owner_email

	return db.update_group(request.db_session, id=group_id, updated_group=group)


def get_group_members(request, group_id):
	members = db.get_users_by_group(request.db_session, group_id)
	return members


def add_group_member(request, group_id, member_id=None, member_email=None):
	if member_id is not None:
		user = db.get_user_by_id(request.db_session, id=member_id)
	elif member_email is not None:
		user = db.get_user(request.db_session, email=member_email)
	else:
		raise Exception("Required Parameter is missing!")
	if user is not None:
		if db.get_group_to_user(request.db_session, group_id, user.id):
			raise BadRequest(request, error_code=ErrorCodes.Validation.UserAlreadyExists, args=user.email)

		return db.add_group_to_user(request.db_session, group_id=group_id, user_id=user.id)
	else:
		raise Exception("User does not exit.")


def delete_group_member(request, group_id, member_id):
	group = db.get_group(request.db_session, id=group_id)
	if group is None:
		raise Exception("Group does not exit.")
	if group.owner.id == member_id:
		raise Exception("Cannot remove group owner from the group!")

	db.delete_group_to_user(request.db_session, group_id=group_id, user_id=member_id)
	return


def search_group_graphs(request, group_id, owner_email, names=None, nodes=None, edges=None, limit=20, offset=0, order='asc', sort='name'):
	sort_attr = getattr(db.Graph, sort if sort is not None else 'name')
	orber_by = getattr(db, order if order is not None else 'desc')(sort_attr)

	total, group_graphs = graphs.controllers.search_graphs_by_group_ids(request,
						group_ids=[group_id],
						owner_email=owner_email,
						names=names,
						nodes=nodes,
						edges=edges,
						limit=limit,
						offset=offset,
						order_by=orber_by)
	return total, group_graphs


def add_group_graph(request, group_id, graph_id):
	return graphs.controllers.add_graph_to_group(request, group_id=group_id, graph_id=graph_id)


def delete_group_graph(request, group_id, graph_id):
	return graphs.controllers.delete_graph_to_group(request, group_id=group_id, graph_id=graph_id)


def get_password_reset_by_code(request, code):
	return db.get_password_reset_by_code(request.db_session, code)

def get_email_confirmation_code(request, code):
	return db.get_email_confirmation_code(request.db_session, code)


def delete_password_reset_code(request, id):
	return db.delete_password_reset(request.db_session, id)


def add_user_to_password_reset(request, email):
	password_reset_code = db.get_password_reset_by_email(request.db_session, email)
	if password_reset_code is not None:
		password_reset_code.code = generate_uid()
		password_reset_code = db.update_password_reset(request.db_session, password_reset_code.id, password_reset_code.serialize())
	else:
		password_reset_code = db.add_password_reset(request.db_session, email)
	return password_reset_code


def send_password_reset_email(request, password_reset_code):
	# Construct email message
	mail_title = 'Password Reset Information for GraphSpace!'
	message = 'Please go to the following url to reset your password: ' + settings.URL_PATH + 'reset_password/?code=' + password_reset_code.code
	email_from = "GraphSpace Admin"

	return send_mail(mail_title, message, email_from, [password_reset_code.email], fail_silently=False)

def send_confirmation_email(request, email, token, email_list_announcement, email_list_user):
	# Construct email message
	mail_title = 'Activate your account for GraphSpace!'
	message = 'Please confirm your email address to complete the registration ' + settings.URL_PATH + 'activate_account/?activation_code=' + token #+ '/?email_list_announcement=' + email_list_announcement + '/?email_list_user=' + email_list_user #str(test_form)
	email_from = "GraphSpace Admin"

	return send_mail(mail_title, message, email_from, [email], fail_silently=False)

#def send_account_creation_confirmation(request, email):
	# Construct confimation message
	#message = 'Congratuation' + email + '. You have created your account successfully.'
#	return HttpResponse(json.dumps(json_success_response(200, message='congraduations')),
#		content_type="application/json")
