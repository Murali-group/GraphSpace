import bcrypt

import applications.graphs as graphs
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
		return add_user(request, email=username, password=password)
	except Exception as e:
		raise e


def add_user(request, email=None, password="graphspace_public_user", is_admin=0):
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

	return db.add_user(request.db_session, email=email, password=bcrypt.hashpw(password, bcrypt.gensalt()), is_admin=is_admin)


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


def search_groups(request, owner_email=None, member_email=None, name=None, description=None, limit=20, offset=0, order='desc', sort='name'):
	if sort == 'name':
		sort_attr = db.Group.name
	elif sort == 'update_at':
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


def search_group_graphs(request, group_id, owner_email, names=None, nodes=None, edges=None, limit=20, offset=0):
	total, group_graphs = graphs.controllers.search_graphs_by_group_ids(request,
						group_ids=[group_id],
						owner_email=owner_email,
						names=names,
						nodes=nodes,
						edges=edges,
						limit=limit,
						offset=offset)
	return total, group_graphs


def add_group_graph(request, group_id, graph_id):
	return graphs.controllers.add_graph_to_group(request, group_id=group_id, graph_id=graph_id)


def delete_group_graph(request, group_id, graph_id):
	return graphs.controllers.delete_graph_to_group(request, group_id=group_id, graph_id=graph_id)