from __future__ import unicode_literals

from applications.users.models import *
from django.conf import settings
from graphspace.mixins import *
from sqlalchemy import ForeignKeyConstraint, text, Enum, Boolean

Base = settings.BASE


# ================== Table Definitions =================== #


class OwnerNotification(IDMixin, TimeStampMixin, EmailMixin, Base):
    __tablename__ = 'owner_notification'

    message = Column(String, nullable=False)
    type = Column(Enum("create", "upload", "update",
                       "delete", name="owner_notification_types"))
    resource = Column(Enum("graph", "layout", "group",
                           name="owner_notification_resource"))
    resource_id = Column(Integer, nullable=False)

    is_read = Column(Boolean, default=False)

    owner_email = Column(String, ForeignKey(
        'user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    owner = relationship("User", back_populates="notification", uselist=False)

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
            'is_read': cls.is_read,
            'is_email_sent': cls.is_email_sent,
            'resource': cls.resource,
            'resource_id': cls.resource_id,
            'owner_email': cls.owner_email,
            'created_at': cls.created_at.isoformat(),
            'updated_at': cls.updated_at.isoformat(),
            'emailed_at': cls.emailed_at.isoformat()
        }
