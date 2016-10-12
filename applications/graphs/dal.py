from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import joinedload

from applications.users.models import *
from graphspace.wrappers import with_session


@with_session
def get_edges(db_session, edges, order=desc(Edge.updated_at), page=0, page_size=10, partial_matching=False):
	edges = [('%%%s%%' % u, '%%%s%%' % v) for u,v in edges] if partial_matching else edges
	filter_group = [and_(Edge.head_node_id.ilike(u), Edge.tail_node_id.ilike(v)) for u,v in edges]
	filter_group.append([and_(Edge.head_node.has(Node.label.ilike(u)), Edge.tail_node.has(Node.label.ilike(v))) for u,v in edges])
	return db_session.query(Graph).options(joinedload('head_node'), joinedload('tail_node')).filter(or_(*filter_group)).order_by(order).limit(page_size).offset(page*page_size)


@with_session
def get_graphs_by_edges_and_nodes_and_names(db_session, group_ids=None,names=None, nodes=None, edges=None, tags=None, order=desc(Graph.updated_at), page=0, page_size=10, partial_matching=False, owner_email=None, is_public=None):
	query = db_session.query(Graph)

	edges = [] if edges is None else edges
	nodes = [] if nodes is None else nodes
	names = [] if names is None else names
	tags = [] if tags is None else tags

	edges = [('%%%s%%' % u, '%%%s%%' % v) for u,v in edges] if partial_matching else edges
	nodes = ['%%%s%%' % node for node in nodes] if partial_matching else nodes
	names = ['%%%s%%' % name for name in names] if partial_matching else names
	tags = ['%%%s%%' % tag for tag in tags]

	graph_filter_group = []
	if is_public is not None:
		graph_filter_group.append(Graph.is_public == is_public)
	if owner_email is not None:
		graph_filter_group.append(Graph.owner_email == owner_email)
	if group_ids is not None:
		query = query.filter(Graph.shared_with_groups.any(Group.id.in_(group_ids)))

	if len(graph_filter_group) > 0:
		query = query.filter(*graph_filter_group)

	names_filter_group = [Graph.name.ilike(name) for name in names]
	tags_filter_group = [GraphTag.name.ilike(tag) for tag in tags]
	nodes_filter_group = [Node.label.ilike(node) for node in nodes]
	nodes_filter_group.extend([Node.name.ilike(node) for node in nodes])
	edges_filter_group = [and_(Edge.head_node.has(Node.label.ilike(u)), Edge.tail_node.has(Node.label.ilike(v))) for u,v in edges]

	options_group = []
	if len(nodes_filter_group) > 0:
		options_group.append(joinedload('nodes'))
	if len(edges_filter_group) > 0:
		options_group.append(joinedload('edges'))
	if len(options_group) > 0:
		query = query.options(*options_group)

	combined_filter_group = []
	if len(nodes_filter_group) > 0:
		combined_filter_group.append(Graph.nodes.any(or_(*nodes_filter_group)))
	if len(edges_filter_group) > 0:
		combined_filter_group.append(Graph.edges.any(or_(*edges_filter_group)))
	if len(names_filter_group) > 0:
		combined_filter_group.append(*names_filter_group)
	if len(tags_filter_group) > 0:
		combined_filter_group.append(*tags_filter_group)

	if len(combined_filter_group) > 0:
		query = query.filter(or_(*combined_filter_group))

	return query.order_by(order).limit(page_size).offset(page*page_size).all()


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
def find_graphs(db_session, group_ids=None, owner_email=None, is_public=None, names=None, nodes=None, edges=None, tags=None, limit=None, offset=None, order_by=desc(Graph.updated_at)):
	query = db_session.query(Graph)

	graph_filter_group = []
	if is_public is not None:
		graph_filter_group.append(Graph.is_public == is_public)
	if owner_email is not None:
		graph_filter_group.append(Graph.owner_email == owner_email)

	if len(graph_filter_group) > 0:
		query = query.filter(*graph_filter_group)

	options_group = []
	if nodes is not None:
		options_group.append(joinedload('nodes'))
	if edges is not None:
		options_group.append(joinedload('edges'))
	if group_ids is not None:
		options_group.append(joinedload('shared_with_groups'))
	if len(options_group) > 0:
		query = query.options(*options_group)

	if group_ids is not None:
		query = query.filter(Graph.shared_with_groups.any(Group.id.in_(group_ids)))

	edges = [] if edges is None else edges
	nodes = [] if nodes is None else nodes
	names = [] if names is None else names
	tags = [] if tags is None else tags

	names_filter = [Graph.name.ilike(name) for name in names]
	tags_filter = [GraphTag.name.ilike(tag) for tag in tags]
	nodes_filter = [Node.label.ilike(node) for node in nodes]
	nodes_filter.extend([Node.name.ilike(node) for node in nodes])
	edges_filter = [and_(Edge.head_node.has(Node.name.ilike(u)), Edge.tail_node.has(Node.name.ilike(v))) for u,v in edges]
	edges_filter.extend([and_(Edge.head_node.has(Node.label.ilike(u)), Edge.tail_node.has(Node.label.ilike(v))) for u,v in edges])

	combined_filter = []
	if len(nodes_filter) > 0:
		combined_filter.append(Graph.nodes.any(or_(*nodes_filter)))
	if len(edges_filter) > 0:
		combined_filter.append(Graph.edges.any(or_(*edges_filter)))
	if len(names_filter) > 0:
		combined_filter.append(*names_filter)
	if len(tags_filter) > 0:
		combined_filter.append(*tags_filter)

	if len(combined_filter) > 0:
		query = query.filter(or_(*combined_filter))

	total = query.count()

	if order_by is not None:
		query = query.order_by(order_by)

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()

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


@with_session
def add_graph_to_group(db_session, group_id, graph_id):
	group_to_graph = GroupToGraph(graph_id=graph_id, group_id=group_id)
	db_session.add(group_to_graph)
	return group_to_graph


@with_session
def delete_graph_to_group(db_session, group_id, graph_id):
	group_to_graph = db_session.query(GroupToGraph).filter(and_(GroupToGraph.group_id == group_id, GroupToGraph.graph_id == graph_id)).one_or_none()
	db_session.delete(group_to_graph)
	return group_to_graph