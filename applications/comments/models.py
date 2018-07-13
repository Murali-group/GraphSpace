from __future__ import unicode_literals

from applications.users.models import *
from applications.graphs.models import *
from django.conf import settings
from graphspace.mixins import *
import json
from sqlalchemy import ForeignKeyConstraint, text, Enum, Boolean

Base = settings.BASE


# ================== Table Definitions =================== #

class Comment(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'comment'

	message = Column(String, nullable=False)
	is_resolved = Column(Integer, nullable=False, default=0)

	owner_email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
	owner = relationship("User", back_populates="owned_comments", uselist=False)

	graph_id = Column(Integer, ForeignKey('graph.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	graph = relationship("Graph", foreign_keys=[graph_id], back_populates="comments", uselist=False)

	layout_id = Column(Integer, ForeignKey('layout.id', ondelete="CASCADE", onupdate="CASCADE"),nullable=True)
	layout = relationship("Layout", foreign_keys=[layout_id], back_populates="comments", uselist=False)

	parent_comment_id = Column(Integer, ForeignKey('comment.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=True)

	nodes = association_proxy('associated_nodes', 'node')
	edges = association_proxy('associated_edges', 'edge')

	constraints = ()
	indices = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls):
		return {
			'id': cls.id,
			'owner_email': cls.owner_email,
			'message': cls.message,
			'is_resolved': cls.is_resolved,
			'graph_id': cls.graph_id,
			'layout_id': cls.layout_id,
			'parent_comment_id': cls.parent_comment_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}

class CommentToNode(TimeStampMixin, Base):
	__tablename__ = 'comment_to_node'

	comment_id = Column(Integer, ForeignKey('comment.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	node_id = Column(Integer, ForeignKey('node.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

	comment = relationship("Comment", backref=backref("associated_nodes", cascade="all, delete-orphan"))
	node = relationship("Node", backref=backref("associated_comments", cascade="all, delete-orphan"))

	indices = (Index('comment2node_idx_comment_id_node_id', 'comment_id', 'node_id'),)
	constraints = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls):
		return {
			'comment_id': cls.comment_id,
			'node_id': cls.node_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}

class CommentToEdge(TimeStampMixin, Base):
	__tablename__ = 'comment_to_edge'

	comment_id = Column(Integer, ForeignKey('comment.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	edge_id = Column(Integer, ForeignKey('edge.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

	comment = relationship("Comment", backref=backref("associated_edges", cascade="all, delete-orphan"))
	edge = relationship("Edge", backref=backref("associated_comments", cascade="all, delete-orphan"))

	indices = (Index('comment2edge_idx_comment_id_edge_id', 'comment_id', 'edge_id'),)
	constraints = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls):
		return {
			'comment_id': cls.comment_id,
			'edge_id': cls.edge_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}