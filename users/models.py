from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from graphspace.mixins import GraphSpaceMixin

Base = declarative_base()


# ================== Table Definitions ===================

class User(GraphSpaceMixin, Base):
	"""
	The class representing the schema of the user table.
	:param email: Email ID of the user.
	:param password: Password of the user.
	:param admin: 1 if the user has admin access else 0.
	"""
	__tablename__ = "user"

	email = Column(String, unique=True)
	password = Column(String, nullable=False)
	is_admin = Column(Integer, nullable=False)
	password_reset_codes = relationship("PasswordResetCode", back_populates="user")


class PasswordResetCode(Base):
	__tablename__ = 'password_reset_code'

	user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	code = Column(String, nullable=False)
	user = relationship("User", back_populates="password_reset_codes", uselist=False)


class Group(Base):
	__tablename__ = 'group'

	group_id = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	owner_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False,
	                  primary_key=True)
	description = Column(String, nullable=False)


class GroupToUser(Base):
	"""The class representing the schema of the group_to_user table."""
	__tablename__ = 'group_to_user'

	user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	group_id = Column(String, ForeignKey('group.group_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	group_owner = Column(String, ForeignKey('group.owner_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
