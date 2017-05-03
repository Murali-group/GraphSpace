from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import asc, desc

from django.utils.datetime_safe import datetime
from graphspace.utils import generate_uid
from graphspace.wrappers import with_session
from models import *


# TODO: Add documentation about exception raised.


@with_session
def add_user(db_session, email, password, is_admin):
	"""
	Add a new user.

	:param db_session: Database session.
	:param email: User ID of the user.
	:param password: Password of the user.
	:param admin: 1 if user has admin access else 0.
	:return: User
	"""
	user = User(email=email, password=password, is_admin = is_admin)
	db_session.add(user)
	return user


@with_session
def get_user(db_session, email):
	"""
	Get a user with given email.

	:param db_session: Database session.
	:param email: email of the user.
	:return: User if email exists else None.
	"""
	return db_session.query(User).filter(User.email == email).one_or_none()


@with_session
def get_user_by_id(db_session, id):
	"""
	Get a user with given email.

	:param db_session: Database session.
	:param id: id of the user.
	:return: User if email exists else None.
	"""
	return db_session.query(User).filter(User.id == id).one_or_none()


@with_session
def update_user(db_session, id, updated_user):
	"""
	Update the user data with given id with the given updated user data.

	:param db_session: Database session.
	:param id: User ID of the user.
	:param updated_user: Updated user data. Data is stored in dictionary format where keys store the column names and values store the updated value.
	:return: User
	"""
	user = db_session.query(User).filter(User.id == id).one_or_none()
	for (key, value) in updated_user.items():
		setattr(user, key, value)
	return user


@with_session
def delete_user(db_session, email):
	"""
	:param db_session: Database session.
	:param email: User ID of the user.
	:return: None
	"""
	user = db_session.query(User).filter(User.email == email)
	db_session.delete(user)
	return


@with_session
def add_password_reset(db_session, email):
	"""
	Add a password reset entry for given user id.
	'code' and 'created' column values are generated programmatically. Their values cannot be set by a user.
	:param db_session: Database session.
	:param email: User ID for which password reset row will be generated.
	:return: None
	"""
	password_reset = PasswordResetCode(email=email, code=generate_uid())
	db_session.add(password_reset)
	return password_reset


@with_session
def get_password_reset_by_email(db_session, email):
	"""
	:param db_session: Database session.
	:param email: User Email
	:return: PasswordReset if email exists else None
	"""
	return db_session.query(PasswordResetCode).filter(PasswordResetCode.email == email).one_or_none()



@with_session
def get_password_reset_by_code(db_session, code):
	"""
	:param db_session: Database session.
	:param code: PasswordReset code
	:return: PasswordReset if email exists else None
	"""
	return db_session.query(PasswordResetCode).filter(PasswordResetCode.code == code).one_or_none()


@with_session
def update_password_reset(db_session, id, updated_password_reset):
	"""
	:param db_session: Database session.
	:param id: primary key in password_reset table.
	:param updated_password_reset: updated password_reset row.
	:return: None
	"""
	password_reset = db_session.query(PasswordResetCode).filter(PasswordResetCode.id == id).one_or_none()
	for (key, value) in updated_password_reset.items():
		setattr(password_reset, key, value)
	return password_reset


@with_session
def delete_password_reset(db_session, id):
	"""
	:param db_session: Database session.
	:param id: primary key in password_reset table.
	:return: None
	"""
	password_reset = db_session.query(PasswordResetCode).filter(PasswordResetCode.id == id).one_or_none()
	db_session.delete(password_reset)
	return


@with_session
def find_users(db_session, email, limit, offset, order_by=asc(User.email)):
	query = db_session.query(User)

	if order_by is not None:
		query = query.order_by(order_by)

	if email is not None:
		query = query.filter(User.email.ilike(email))

	query = query.filter(User.email.notilike('%public_user%'));

	total = query.count()

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()


@with_session
def add_group(db_session, name, owner_email, description):
	"""
	:param db_session: Database session.
	:param name: Name of the group
	:param owner_email: ID of user who owns the group
	:param description: Description of the group
	:return: None
	"""
	group = Group(name=name, owner_email=owner_email, description = description, invite_code=generate_uid(size=10))
	db_session.add(group)
	return group


@with_session
def get_group(db_session, id):
	"""
	Get group by group id.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:return: Group if id exists else None
	"""
	return db_session.query(Group).filter(Group.id == id).one_or_none()


@with_session
def update_group(db_session, id, updated_group):
	"""
	Update group row entry.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:param updated_group: Updated group row entry
	:return: Group if id exists else None
	"""
	group = db_session.query(Group).filter(Group.id == id).one_or_none()
	for (key, value) in updated_group.items():
		setattr(group, key, value)
	return group


@with_session
def delete_group(db_session, id):
	"""
	Delete group from Group table.
	:param db_session: Database session.
	:param id: Unique ID of the group
	:return: None
	"""
	group = db_session.query(Group).filter(Group.id == id).one_or_none()
	db_session.delete(group)
	return


@with_session
def get_group_to_user(db_session, group_id, user_id):
	"""
	:param db_session: Database session.
	:param group_id: Unique ID of the group
	:param user_id: Unique user ID of a member of the group
	:return: GroupToUser if entry exists else None
	"""
	return db_session.query(GroupToUser).filter(and_(GroupToUser.group_id == group_id, GroupToUser.user_id == user_id)).one_or_none()


@with_session
def add_group_to_user(db_session, group_id, user_id):
	"""
	:param db_session: Database session.
	:param group_id: Unique ID of the group
	:param user_id: Unique ID of a member of the group
	:return: GroupToUser if entry exists else None
	"""
	group_to_user = GroupToUser(user_id=user_id, group_id=group_id)
	db_session.add(group_to_user)
	return group_to_user


@with_session
def delete_group_to_user(db_session, group_id, user_id):
	"""
	:param db_session: Database session.
	:param group_id: Unique ID of the group
	:param id: Unique ID of a member of the group
	:return: None
	"""
	group_to_user = db_session.query(GroupToUser).filter(and_(GroupToUser.group_id == group_id, GroupToUser.user_id == user_id)).one_or_none()
	db_session.delete(group_to_user)
	return

@with_session
def get_groups_by_member_id(db_session, member_id):
	"""
	Returns all groups where user with given user_id is a member.
	:param db_session: Database session.
	:param member_id: ID of a user who is a member of one or many groups.
	:return: list of Groups
	"""
	return [group_to_user.group for group_to_user in db_session.query(GroupToUser).filter(GroupToUser.user_id == member_id).all()]


@with_session
def get_groups_by_owner_id(db_session, owner_id):
	"""
	Returns all groups where user with given ID is the owner.

	:param db_session: Database session.
	:param owner_id: email of a user who owns one or many groups.
	:return: list of Groups
	"""
	user = db_session.query(User).filter(User.id == owner_id).one_or_none()
	if user is not None:
		return user.owned_groups
	else:
		return None


# @with_session
def get_users_by_group(db_session, group_id):
	"""
	Returns all users who are member of a group with given group_id.
	:param db_session: Database session.
	:param group_owner: Unique ID of the user who owns the group.
	:param group_id: Unique ID of the group.
	:return: list of Users
	"""
	group = db_session.query(Group).filter(Group.id == group_id).one_or_none()
	if group is not None:
		return list(group.members)
	else:
		raise Exception("Group Not Found")


@with_session
def find_groups(db_session, owner_email, member_email, name, description, graph_ids, limit, offset, order_by=asc(Group.name)):
	query = db_session.query(Group)

	if order_by is not None:
		query = query.order_by(order_by)

	if owner_email is not None:
		query = query.filter(Group.owner_email.ilike(owner_email))

	if name is not None:
		query = query.filter(Group.name.ilike(name))

	if description is not None:
		query = query.filter(Group.description.ilike(description))

	if member_email is not None:
		query = query.options(joinedload('member_users'))
		query = query.filter(Group.members.any(User.email == member_email))

	if graph_ids is not None and len(graph_ids) > 0:
		query = query.options(joinedload('shared_graphs'))
		query = query.filter(Group.graphs.any(Graph.id.in_(graph_ids)))

	total = query.count()

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()
