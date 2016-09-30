from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import joinedload

from models import *
from django.utils.datetime_safe import datetime
from graphspace.utils import generate_uid
from sqlalchemy.orm.exc import NoResultFound
from graphspace.wrappers import with_session


@with_session
def get_edges(db_session, edges, order=desc(Edge.updated_at), page=0, page_size=10, partial_matching=False):
	edges = [('%%%s%%' % u, '%%%s%%' % v) for u,v in edges] if partial_matching else edges
	filter_group = [and_(Edge.head_node_id.like(u), Edge.tail_node_id.like(v)) for u,v in edges]
	filter_group.append([and_(Edge.head_node.has(Node.label.like(u)), Edge.tail_node.has(Node.label.like(v))) for u,v in edges])
	return db_session.query(Graph).options(joinedload('head_node'), joinedload('tail_node')).filter(or_(*filter_group)).order_by(order).limit(page_size).offset(page*page_size)


@with_session
def get_graphs_by_edges_or_nodes(db_session, names=None, nodes=None, edges=None, order=desc(Edge.updated_at), page=0, page_size=10, partial_matching=False):

	edges = [] if edges is None else edges
	nodes = [] if nodes is None else nodes
	names = [] if names is None else names

	edges = [('%%%s%%' % u, '%%%s%%' % v) for u,v in edges] if partial_matching else edges
	nodes = ['%%%s%%' % node for node in nodes] if partial_matching else nodes
	names = ['%%%s%%' % name for name in names] if partial_matching else names

	graph_filter_group = [Graph.name.like(name) for name in names]
	nodes_filter_group = [Node.label.like(node) for node in nodes]
	nodes_filter_group.append([Node.name.like(node) for node in nodes])
	edges_filter_group = [and_(Edge.head_node.has(Node.label.like(u)), Edge.tail_node.has(Node.label.like(v))) for u,v in edges]

	return db_session.query(Graph).options(joinedload('nodes'), joinedload('edges'))\
		.filter(or_(Graph.edges.any(or_(*edges_filter_group)), Graph.nodes.any(or_(*nodes_filter_group), *graph_filter_group)))\
		.order_by(order).limit(page_size).offset(page*page_size)


@with_session
def add_graph(db_session, name, owner_email, json, is_public=0, default_layout_id=None):
	graph = Graph(name=name, owner_email=owner_email, json=json, is_public=is_public, default_layout_id=default_layout_id)
	db_session.add(graph)
	return graph


@with_session
def get_graph(db_session, owner_email, name):
	return db_session.query(Graph).filter(and_(Graph.owner_email == owner_email, Graph.name == name)).one_or_none()


@with_session
def get_graph_by_id(db_session, id):
	return db_session.query(Graph).filter(Graph.id == id).one_or_none()


@with_session
def add_edge(db_session, graph_id, head_node_id, tail_node_id, name, is_directed):
	edge = Edge(name=name, graph_id=graph_id, head_node_id=head_node_id, tail_node_id = tail_node_id, is_directed = is_directed)
	db_session.add(edge)
	return edge


@with_session
def add_node(db_session, graph_id, name, label):
	node = Node(name=name, graph_id=graph_id, label=label)
	db_session.add(node)
	return node


@with_session
def get_tag_by_name(db_session, name):
	return db_session.query(GraphTag).filter(GraphTag.name == name).one_or_none()


@with_session
def add_tag_to_graph(db_session, graph_id, tag_id):
	graph_to_tag = GraphToTag(graph_id=graph_id, tag_id=tag_id)
	db_session.add(graph_to_tag)
	return graph_to_tag

@with_session
def add_tag(db_session, name):
	tag = GraphTag(name = name)
	db_session.add(tag)
	return tag

@with_session
def get_layout(db_session, owner_email, name, graph_id):
	return db_session.query(Layout).filter(and_(Layout.owner_email == owner_email, Layout.name == name, Layout.graph_id == graph_id)).one_or_none()