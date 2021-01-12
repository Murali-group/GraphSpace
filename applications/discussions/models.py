from __future__ import unicode_literals

import json
from applications.users.models import *
from applications.comments.models import *
from django.conf import settings
from graphspace.mixins import *
from sqlalchemy import ForeignKeyConstraint, text, Enum, Boolean
from sqlalchemy import String, ForeignKey, UniqueConstraint
Base = settings.BASE


# ================== Table Definitions =================== #

class Discussion(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'discussion'

	topic = Column(String, nullable=False)
	description = Column(String, nullable=True)
	is_closed = Column(Integer, nullable=False, default=0)

	owner_email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	owner = relationship("User", back_populates="owned_discussions", uselist=False)

	group_id = Column(Integer, ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	group = relationship("Group", back_populates="group_discussions", uselist=False)

	comments = association_proxy('associated_comments', 'comment')

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
			'topic': cls.topic,
			'description': cls.description,
			'is_closed': cls.is_closed,
			'group_id': cls.group_id,
			'group_owner_email': cls.group.owner_email,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}

class CommentToDiscussion(TimeStampMixin, Base):
	__tablename__ = 'comment_to_discussion'

	discussion_id = Column(Integer, ForeignKey('discussion.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	comment_id = Column(Integer, ForeignKey('comment.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

	discussion = relationship("Discussion", backref=backref("associated_comments", cascade="all, delete-orphan"))
	comment = relationship("Comment", backref=backref("associated_discussion", cascade="all, delete-orphan"))


	indices = (Index('comment2discussion_idx_comment_id_discussion_id', 'comment_id', 'discussion_id'),)
	constraints = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		return {
			'comment_id': cls.comment_id,
			'discussion_id': cls.discussion_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}
