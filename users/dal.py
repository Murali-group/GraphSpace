import models
import graphs.util.db_init as db_init

data_connection = db_init.db


def add_user(user_id="public_user@graphspace.com", password="public", admin=0):
	"""

	:param user_id: User ID of the user. Default value is dynamically generated user id.
	:param password: Password of the user. Default value is "public".
	:param admin: 1 if user has admin access else 0. Default value is 0.
	:return: None
	"""
	db_session = data_connection.new_session()
	public_user = models.User(user_id, password, admin)
	db_session.add(public_user)
	db_session.commit()
	db_session.close()


def get_user(user_id):
	"""

	:param user_id:
	:return: User if user_id exists else None
	"""


def update_user(user_id, updated_user):
	"""

	:param user_id:
	:param updated_user:
	:return: None
	"""


def delete_user(user_id):
	"""

	:param user_id:
	:return: None
	"""


def add_password_reset(user_id):
	"""
	Add a password reset entry for given user id.
	'id', 'code' and 'created' column values are generated programmatically. Their values cannot be set by a user.

	:param user_id: User ID for which password reset row will be generated.
	:return: None
	"""


def get_password_reset_by_code(code):
	"""

	:param code: Password reset code
	:return: PasswordReset if code exists else None
	"""


def update_password_reset(id, updated_user):
	"""

	:param id: primary key in password_reset table.
	:param updated_user: updated password_reset row.
	:return: None
	"""


def add_group(group_id, name, owner_id, description):
	"""

	:param group_id: Unique ID of the group
	:param name: Name of the group
	:param owner_id: ID of user who owns the group
	:param description: Description of the group
	:return: None
	"""


def get_group(group_id):
	"""
	Get group by group id.

	:param group_id: Unique ID of the group
	:return: Group if group_id exists else None
	"""


def update_group(group_id, updated_group):
	"""
	Update group row entry.

	:param group_id: Unique ID of the group
	:param updated_group: Updated group row entry
	:return: None
	"""


def delete_group(group_id):
	"""
	Delete group from Group table.
	:param group_id: Unique ID of the group
	:return: None
	"""


def add_group_to_user(group_id, user_id, group_owner):
	"""

	:param group_owner: Unique ID of the user who owns the group.
	:param group_id: Unique ID of the group
	:param user_id: Unique ID of a member of the group
	:return: None
	"""


def delete_group_to_user(group_id, user_id, group_owner):
	"""
	:param group_owner: Unique ID of the user who owns the group.
	:param group_id: Unique ID of the group
	:param user_id: Unique ID of a member of the group
	:return: None
	"""


def get_groups_by_user_id(user_id):
	"""
	Returns all groups where user with give user_id is a member.

	:param user_id: user_id of a user who is a member of one or many groups.
	:return: list of Groups
	"""


def get_groups_by_owner_id(owner_id):
	"""
	Returns all groups where user with give user_id is a owner.

	:param owner_id: user_id of a user who owns one or many groups.
	:return: list of Groups
	"""


def get_users_by_group(group_id, group_owner):
	"""
	Returns all users who are member of a group with given group_id.

	:param group_owner: Unique ID of the user who owns the group.
	:param group_id: Unique ID of the group.
	:return: list of Users
	"""



