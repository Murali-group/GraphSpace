from __future__ import unicode_literals

from applications.users.models import *
from django.conf import settings
from graphspace.mixins import *
import json
from sqlalchemy import ForeignKeyConstraint, text, Enum, Boolean
from sqlalchemy import String, ForeignKey, UniqueConstraint
Base = settings.BASE


# ================== Table Definitions =================== #

class Discussion(IDMixin, TimeStampMixin, Base):
    __tablename__ = 'discussion'

    message = Column(String, nullable=False)
    is_resolved = Column(Integer, nullable=False, default=0)
    topic = Column(String, nullable=True)

    owner_email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="owned_discussions", uselist=False)

    group_id = Column(Integer, ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    group = relationship("Group", back_populates="group_discussions", uselist=False)

    parent_discussion_id = Column(Integer, ForeignKey('discussion.id', ondelete="CASCADE", onupdate="CASCADE"),
                                  nullable=True)
    constraints = (UniqueConstraint('topic', 'group_id', name='_discussion_uc_topic_group_id'),)
    indices = ()

    @declared_attr
    def __table_args__(cls):
        args = cls.constraints + cls.indices
        return args

    def serialize(cls, **kwargs):
        return {
            'id': cls.id,
            'owner_email': cls.owner_email,
            'message': cls.message,
            'topic': cls.topic,
            'is_resolved': cls.is_resolved,
            'group_id': cls.group_id,
            'parent_discussion_id': cls.parent_discussion_id,
            'group_owner_email': cls.group.owner_email,
            'created_at': cls.created_at.isoformat(),
            'updated_at': cls.updated_at.isoformat()
        }


