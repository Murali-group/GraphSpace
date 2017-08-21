from __future__ import unicode_literals

from applications.users.models import *
from django.conf import settings
from graphspace.mixins import *
import json
from sqlalchemy import ForeignKeyConstraint, text

Base = settings.BASE


# ================== Table Definitions =================== #


class Graph(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'graph'

	name = Column(String, nullable=False)
	owner_email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	graph_json = Column(String, nullable=False)
	style_json = Column(String, nullable=False)
	is_public = Column(Integer, nullable=False, default=0)
	default_layout_id = Column(Integer, ForeignKey('layout.id', ondelete="CASCADE", onupdate="CASCADE"),
	                           nullable=True)

	owner = relationship("User", back_populates="owned_graphs", uselist=False)
	default_layout = relationship("Layout", foreign_keys=[default_layout_id], back_populates="default_layout_graph",
	                              uselist=False)

	layouts = relationship("Layout", foreign_keys="Layout.graph_id", back_populates="graph",
	                       cascade="all, delete-orphan")
	edges = relationship("Edge", back_populates="graph", cascade="all, delete-orphan")
	nodes = relationship("Node", back_populates="graph", cascade="all, delete-orphan")

	groups = association_proxy('shared_with_groups', 'group')
	tags = association_proxy('graph_tags', 'tag')

	constraints = (
		UniqueConstraint('name', 'owner_email', name='_graph_uc_name_owner_email'),
	)
	indices = (
		Index('graph_idx_name', text("name gin_trgm_ops"), postgresql_using="gin"),
	)

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		if 'summary' in kwargs and kwargs['summary']:
			return {
				'id': cls.id,
				'owner_email': cls.owner_email,
				'name': cls.name,
				'is_public': cls.is_public,
				'tags': [tag.name for tag in cls.tags],
				'default_layout_id': cls.default_layout_id,
				'created_at': cls.created_at.isoformat(),
				'updated_at': cls.updated_at.isoformat()
			}
		else:
			return {
				'id': cls.id,
				'owner_email': cls.owner_email,
				'name': cls.name,
				'graph_json': json.loads(cls.graph_json),
				'style_json': json.loads(cls.style_json),
				'is_public': cls.is_public,
				'tags': [tag.name for tag in cls.tags],
				'default_layout_id': cls.default_layout_id,
				'created_at': cls.created_at.isoformat(),
				'updated_at': cls.updated_at.isoformat()
			}


class Edge(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'edge'

	graph_id = Column(Integer, ForeignKey('graph.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	head_node_id = Column(Integer, ForeignKey('node.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	tail_node_id = Column(Integer, ForeignKey('node.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	tail_node_name = Column(String, nullable=False)
	head_node_name = Column(String, nullable=False)
	tail_node_label = Column(String, nullable=False)
	head_node_label = Column(String, nullable=False)
	is_directed = Column(Integer, nullable=False)
	name = Column(String, nullable=False)

	graph = relationship("Graph", back_populates="edges", uselist=False)
	head_node = relationship("Node", foreign_keys=[head_node_id], back_populates="source_edges", uselist=False)
	tail_node = relationship("Node", foreign_keys=[tail_node_id], back_populates="target_edges", uselist=False)

	constraints = (
		UniqueConstraint('graph_id', 'head_node_id', 'tail_node_id',
		                 name='_edge_uc_graph_id_head_node_id_tail_node_id'),
		UniqueConstraint('graph_id', 'name', name='_edge_uc_graph_id_name'),
		ForeignKeyConstraint(['head_node_id', 'head_node_name'], ['node.id', 'node.name'], ondelete="CASCADE",
		                     onupdate="CASCADE"),
		ForeignKeyConstraint(['head_node_id', 'head_node_label'], ['node.id', 'node.label'], ondelete="CASCADE",
		                     onupdate="CASCADE"),
		ForeignKeyConstraint(['tail_node_id', 'tail_node_name'], ['node.id', 'node.name'], ondelete="CASCADE",
		                     onupdate="CASCADE"),
		ForeignKeyConstraint(['tail_node_id', 'tail_node_label'], ['node.id', 'node.label'], ondelete="CASCADE",
		                     onupdate="CASCADE"),
	)

	indices = (
		Index('edge_idx_head_label_tail_label', text("head_node_label, tail_node_label gin_trgm_ops"),
		      postgresql_using="gin"),
		Index('edge_idx_head_name_tail_name', text("head_node_name, tail_node_name gin_trgm_ops"),
		      postgresql_using="gin"),
		Index('edge_idx_head_id_tail_id', "head_node_id", "tail_node_label"),
	)

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		return {
			'id': cls.id,
			'name': cls.name,
			'is_directed': cls.is_directed,
			'head_node': cls.head_node.serialize(),
			'tail_node': cls.tail_node.serialize(),
			'graph_id': cls.graph_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}


class Node(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'node'

	name = Column(String, nullable=False)
	label = Column(String, nullable=False)
	graph_id = Column(Integer, ForeignKey('graph.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

	graph = relationship("Graph", back_populates="nodes", uselist=False)
	source_edges = relationship("Edge", foreign_keys="Edge.head_node_id", back_populates="head_node",
	                            cascade="all, delete-orphan")
	target_edges = relationship("Edge", foreign_keys="Edge.tail_node_id", back_populates="tail_node",
	                            cascade="all, delete-orphan")

	constraints = (
		UniqueConstraint('graph_id', 'name', name='_node_uc_graph_id_name'),
		UniqueConstraint('id', 'name', name='_node_uc_id_name'),
		UniqueConstraint('id', 'label', name='_node_uc_id_label'),
	)

	indices = (
		Index('node_idx_name', text("name gin_trgm_ops"), postgresql_using="gin"),
		Index('node_idx_label', text("label gin_trgm_ops"), postgresql_using="gin"),
	)

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		return {
			'id': cls.id,
			'name': cls.name,
			'label': cls.label,
			'graph_id': cls.graph_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}


class GroupToGraph(TimeStampMixin, Base):
	__tablename__ = 'group_to_graph'

	graph_id = Column(Integer, ForeignKey('graph.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	group_id = Column(Integer, ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

	graph = relationship("Graph", backref=backref("shared_with_groups", cascade="all, delete-orphan"))
	group = relationship("Group", backref=backref("shared_graphs", cascade="all, delete-orphan"))

	indices = (Index('group2graph_idx_graph_id_group_id', 'graph_id', 'group_id'),)
	constraints = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		return {
			'group_id': cls.group_id,
			'graph_id': cls.graph_id,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}


class Layout(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'layout'

	name = Column(String, nullable=False)
	owner_email = Column(String, ForeignKey('user.email', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	graph_id = Column(Integer, ForeignKey('graph.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
	positions_json = Column(String, nullable=False)
	style_json = Column(String, nullable=False)
	is_shared = Column(Integer, nullable=False, default=0)
	original_json = Column(String, nullable=True)

	graph = relationship("Graph", foreign_keys=[graph_id], back_populates="layouts", uselist=False)
	owner = relationship("User", back_populates="owned_layouts", uselist=False)

	default_layout_graph = relationship("Graph", foreign_keys="Graph.default_layout_id",
	                                    back_populates="default_layout", cascade="all, delete-orphan",
	                                    uselist=False)

	constraints = (
		UniqueConstraint('name', 'graph_id', 'owner_email', name='_layout_uc_name_graph_id_owner_email'),)
	indices = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args

	def serialize(cls, **kwargs):
		return {
			'id': cls.id,
			'name': cls.name,
			'owner_email': cls.owner_email,
			'graph_id': cls.graph_id,
			'positions_json': cls.positions_json,
			'style_json': cls.style_json,
			'is_shared': cls.is_shared,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}

	# The id of the user who created the layout. The foreign key constraint ensures
	# this person is present in the 'user' table. Not that owner_id need not be the
	# same as user_id since (graph_id, user_id) uniquely identify the graph.
	# In other words, the owner_id can be the person other than the one who created
	# the graph (user_id). An implicit rule is that owner_id must belong to some
	# group that this graph belongs to. However, the database does not enforce this
	# constraint explicitly.
	# TODO: Add a database constraint that checks this rule.


class GraphTag(IDMixin, TimeStampMixin, Base):
	__tablename__ = 'graph_tag'

	name = Column(String, nullable=False, unique=True)

	graphs = association_proxy('tagged_graphs', 'graph')

	def serialize(cls, **kwargs):
		return {
			'id': cls.id,
			'name': cls.name,
			'created_at': cls.created_at.isoformat(),
			'updated_at': cls.updated_at.isoformat()
		}


class GraphToTag(TimeStampMixin, Base):
	__tablename__ = 'graph_to_tag'

	graph_id = Column(Integer, ForeignKey('graph.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
	tag_id = Column(Integer, ForeignKey('graph_tag.id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

	graph = relationship("Graph", backref=backref("graph_tags", cascade="all, delete-orphan"), uselist=False)
	tag = relationship("GraphTag", backref=backref("tagged_graphs", cascade="all, delete-orphan"), uselist=False)

	indices = (Index('graph2tag_idx_graph_id_tag_id', 'graph_id', 'tag_id'),)
	constraints = ()

	@declared_attr
	def __table_args__(cls):
		args = cls.constraints + cls.indices
		return args
