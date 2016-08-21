from __future__ import unicode_literals
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from graphspace.mixins import *
from django.conf import settings
from graphs.models import *

Base = settings.BASE

# ================== Table Definitions ===================


class User(IDMixin, TimeStampMixin, Base):
	"""
	The class representing the schema of the user table.
	:param email: Email ID of the user.
	:param password: Password of the user.
	:param admin: 1 if the user has admin access else 0.
	"""
	__tablename__ = "user"

	email = Column(String, nullable=False, unique=True, index=True)
	password = Column(String, nullable=False)
	is_admin = Column(Integer, nullable=False)

	password_reset_codes = relationship("PasswordResetCode", back_populates="user", cascade="all, delete-orphan")
	owned_groups = relationship("Group", back_populates="owner", cascade="all, delete-orphan")
	owned_graphs = relationship("Graph", back_populates="owner", cascade="all, delete-orphan")
	owned_layouts = relationship("Layout", back_populates="owner", cascade="all, delete-orphan")

	member_groups = association_proxy('user_groups', 'group')

	constraints = ()
	indices = ()

	@declared_attr
	def __table_args__(cls):
		args = tuple() + cls.constraints + cls.indices
		return args


class PasswordResetCode(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'password_reset_code'

	email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
	code = Column(String, nullable=False)
	user = relationship("User", back_populates="password_reset_codes", uselist=False)

	constraints = (UniqueConstraint('email', 'code', name='_password_reset_code_uc_email_code'),)
	indices = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args


class Group(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'group'

	name = Column(String, nullable=False)
	owner_email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	description = Column(String, nullable=False)

	owner = relationship("User", back_populates="owned_groups", uselist=False)
	members = association_proxy('member_users', 'user')
	graphs = association_proxy('shared_graphs', 'graph')

	constraints = (UniqueConstraint('name', 'owner_email', name='_group_uc_name_owner_email'),)
	indices = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args


class GroupToUser(TimeStampMixin, Base):
	"""The class representing the schema of the group_to_user table."""
	__tablename__ = 'group_to_user'

	user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	group_id = Column(Integer, ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

	user = relationship("User", backref=backref("user_groups", cascade="all, delete-orphan"), uselist=False)
	group = relationship("Group", backref=backref("member_users", cascade="all, delete-orphan"), uselist=False)

	indices = (Index('group2user_idx_user_id_group_id', 'user_id', 'group_id'),)
	constraints = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args
