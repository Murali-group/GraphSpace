from __future__ import unicode_literals

from applications.users.models import *
from django.conf import settings
from graphspace.mixins import *
from sqlalchemy import ForeignKeyConstraint, text, Enum

Base = settings.BASE


# ================== Table Definitions =================== #


class Notification(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'notification'

	message = Column(String, nullable=False)
	type = Column(Enum("owner", "group", "watching", name="notification_types"))

	owner_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
	owner = relationship("User", back_populates="notification", uselist=False)

	group_id = Column(Integer, ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
	group = relationship("Group", back_populates="notification", uselist=False)

	constraints = ()
	indices = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls):
		return {
			'id': cls.id,
			'message': cls.message,
			'type': cls.type,
			'owner_id': cls.owner_id,
			'group_id': cls.group_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}