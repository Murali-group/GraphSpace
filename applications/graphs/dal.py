from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import joinedload, subqueryload

from applications.users.models import *
from graphspace.wrappers import with_session
from sqlalchemy.orm import defer, undefer


@with_session
def get_edges(db_session, edges, order=desc(Edge.updated_at), page=0, page_size=10, partial_matching=False):
	edges = [('%%%s%%' % u, '%%%s%%' % v) for u, v in edges] if partial_matching else edges
	filter_group = [and_(Edge.head_node_id.ilike(u), Edge.tail_node_id.ilike(v)) for u, v in edges]
	filter_group.append(
		[and_(Edge.head_node.has(Node.label.ilike(u)), Edge.tail_node.has(Node.label.ilike(v))) for u, v in edges])
	return db_session.query(Graph).options(joinedload('head_node'), joinedload('tail_node')).filter(
		or_(*filter_group)).order_by(order).limit(page_size).offset(page * page_size)


@with_session
def get_graphs_by_edges_and_nodes_and_names(db_session, group_ids=None, names=None, nodes=None, edges=None, tags=None,
                                            order=desc(Graph.updated_at), page=0, page_size=10, partial_matching=False,
                                            owner_email=None, is_public=None):
	query = db_session.query(Graph)

	edges = [] if edges is None else edges
	nodes = [] if nodes is None else nodes
	names = [] if names is None else names
	tags = [] if tags is None else tags

	edges = [('%%%s%%' % u, '%%%s%%' % v) for u, v in edges] if partial_matching else edges
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
	edges_filter_group = [and_(Edge.head_node.has(Node.name.ilike(u)), Edge.tail_node.has(Node.name.ilike(v))) for u, v
	                      in edges]
	edges_filter_group.extend(
		[and_(Edge.tail_node.has(Node.name.ilike(u)), Edge.head_node.has(Node.name.ilike(v))) for u, v in edges])
	edges_filter_group.extend(
		[and_(Edge.head_node.has(Node.label.ilike(u)), Edge.tail_node.has(Node.label.ilike(v))) for u, v in edges])
	edges_filter_group.extend(
		[and_(Edge.tail_node.has(Node.label.ilike(u)), Edge.head_node.has(Node.label.ilike(v))) for u, v in edges])

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

	return query.order_by(order).limit(page_size).offset(page * page_size).all()


@with_session
def add_graph(db_session, name, owner_email, graph_json, style_json, is_public=0, default_layout_id=None):
	graph = Graph(name=name, owner_email=owner_email, graph_json=graph_json, style_json=style_json, is_public=is_public,
	              default_layout_id=default_layout_id)
	db_session.add(graph)
	return graph


@with_session
def update_graph(db_session, id, updated_graph):
	"""
	Update graph row entry.
	:param db_session: Database session.
	:param id: Unique ID of the graph
	:param updated_graph: Updated graph row entry
	:return: Graph if id exists else None
	"""
	graph = db_session.query(Graph).filter(Graph.id == id).one_or_none()
	for (key, value) in updated_graph.items():
		setattr(graph, key, value)
	return graph


@with_session
def get_graph(db_session, owner_email, name):
	return db_session.query(Graph).filter(and_(Graph.owner_email == owner_email, Graph.name == name)).one_or_none()


@with_session
def delete_graph(db_session, id):
	"""
	Delete group from Graph table.
	:param db_session: Database session.
	:param id: Unique ID of the graph
	:return: None
	"""
	graph = db_session.query(Graph).filter(Graph.id == id).one_or_none()
	db_session.delete(graph)
	return


@with_session
def get_graph_by_id(db_session, id):
	return db_session.query(Graph).filter(Graph.id == id).one_or_none()

# Returns a list of all graph id's that have been shared with a group
@with_session
def get_graphs_by_group(db_session, group_id):
	return db_session.query(GroupToGraph.graph_id).filter(and_(GroupToGraph.group_id == group_id)).all()


@with_session
def find_graphs(db_session, owner_email=None, group_ids=None, graph_ids=None, is_public=None, names=None, nodes=None,
                edges=None,
                tags=None, limit=None, offset=None, order_by=desc(Graph.updated_at)):

	# This function is no longer being called by 'My Graphs' or 'Public Graphs'.
	# It was last used in commit aea7096882d2ad0e0ec3b7ab9c0fdfa11bb4659e
	# This is because the logic for retrieving Graphs owned by owner_email and those that are public
	# is done solely inside elasticsearch. We no longer access the Postgres database.

	query = db_session.query(Graph)
	query = query.options(defer("graph_json")).options(defer("style_json"))

	graph_filter_group = []
	if is_public is not None:
		graph_filter_group.append(Graph.is_public == is_public)
	if owner_email is not None:
		graph_filter_group.append(Graph.owner_email == owner_email)

	if len(graph_filter_group) > 0:
		query = query.filter(*graph_filter_group)

	if graph_ids is not None:
		query = query.filter(Graph.id.in_(graph_ids))

	options_group = []
	if tags is not None and len(tags) > 0:
		options_group.append(joinedload('graph_tags'))
	if nodes is not None and len(nodes) > 0:
		options_group.append(subqueryload('nodes'))
	if edges is not None and len(edges) > 0:
		options_group.append(subqueryload(Graph.edges))
	if group_ids is not None and len(group_ids) > 0:
		options_group.append(joinedload('shared_with_groups'))
	if len(options_group) > 0:
		query = query.options(*options_group)

	if group_ids is not None:
		query = query.filter(Graph.groups.any(Group.id.in_(group_ids)))

	edges = [] if edges is None else edges
	nodes = [] if nodes is None else nodes
	names = [] if names is None else names
	tags = [] if tags is None else tags

	elements_filter = []
	names_filter = []

	if len(names) > 0:
		names_filter = [Graph.name.ilike(name) for name in names]

	if len(nodes) > 0:
		elements_filter.extend([Graph.nodes.any(or_(Node.label.ilike(node), Node.name.ilike(node))) for node in nodes])

	if len(edges) > 0:
		for u, v in edges:
			edge_filter = [
				and_(Edge.head_node_name.ilike(u), Edge.tail_node_name.ilike(v)),
				and_(Edge.tail_node_name.ilike(u), Edge.head_node_name.ilike(v)),
				and_(Edge.head_node_label.ilike(u), Edge.tail_node_label.ilike(v)),
				and_(Edge.tail_node_label.ilike(u), Edge.head_node_label.ilike(v))
			]
			elements_filter.append(Graph.edges.any(or_(*edge_filter)))

	combinded_filter = []
	if len(elements_filter) > 0:
		combinded_filter.append(and_(*elements_filter))
	if len(names_filter) > 0:
		combinded_filter.append(or_(*names_filter))
	if len(combinded_filter) > 0:
		query = query.filter(or_(*combinded_filter))

	if len(tags) > 0:
		for tag in tags:
			query = query.filter(Graph.tags.any(GraphTag.name.ilike(tag)))

	total = query.count()

	if order_by is not None:
		query = query.order_by(order_by)

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()


@with_session
def get_edge_by_id(db_session, id):
	return db_session.query(Edge).filter(Edge.id == id).one_or_none()


@with_session
def add_edge(db_session, graph_id, head_node_id, tail_node_id, name, is_directed):
	head_node = get_node_by_id(db_session, head_node_id)
	tail_node = get_node_by_id(db_session, tail_node_id)

	edge = Edge(name=name, graph_id=graph_id,
	            head_node_id=head_node_id, tail_node_id=tail_node_id,
	            head_node_name=head_node.name, tail_node_name=tail_node.name,
	            head_node_label=head_node.label, tail_node_label=tail_node.label,
	            is_directed=is_directed)
	db_session.add(edge)
	return edge


@with_session
def update_edge(db_session, id, updated_edge):
	edge = db_session.query(Edge).filter(Edge.id == id).one_or_none()
	for (key, value) in updated_edge.items():
		setattr(edge, key, value)
	return edge


@with_session
def delete_edge(db_session, id):
	edge = db_session.query(Edge).filter(Edge.id == id).one_or_none()
	db_session.delete(edge)
	return edge


@with_session
def get_node_by_id(db_session, id):
	return db_session.query(Node).filter(Node.id == id).one_or_none()


@with_session
def add_node(db_session, graph_id, name, label):
	node = Node(name=name, graph_id=graph_id, label=label)
	db_session.add(node)
	return node


@with_session
def update_node(db_session, id, updated_node):
	node = db_session.query(Node).filter(Node.id == id).one_or_none()
	for (key, value) in updated_node.items():
		setattr(node, key, value)
	return node


@with_session
def delete_node(db_session, id):
	node = db_session.query(Node).filter(Node.id == id).one_or_none()
	db_session.delete(node)
	return node


@with_session
def remove_nodes_by_graph_id(db_session, graph_id):
	db_session.query(Node).filter(Node.graph_id == graph_id).delete()


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
	tag = GraphTag(name=name)
	db_session.add(tag)
	return tag


@with_session
def get_layout(db_session, owner_email, name, graph_id):
	return db_session.query(Layout).filter(
		and_(Layout.owner_email == owner_email, Layout.name == name, Layout.graph_id == graph_id)).one_or_none()

"""
Returns a list of users that a graph has been shared with by
creating a join between GroupToGraph and GroupToUser
"""
@with_session
def get_graphs_to_users(db_session, graph_id):
	return db_session.query(GroupToUser.user_id).filter(
		and_(GroupToGraph.graph_id == graph_id, GroupToGraph.group_id == GroupToUser.group_id)).all()

@with_session
def add_graph_to_group(db_session, group_id, graph_id):
	group_to_graph = GroupToGraph(graph_id=graph_id, group_id=group_id)
	db_session.add(group_to_graph)
	return group_to_graph


@with_session
def delete_graph_to_group(db_session, group_id, graph_id):
	group_to_graph = db_session.query(GroupToGraph).filter(
		and_(GroupToGraph.group_id == group_id, GroupToGraph.graph_id == graph_id)).one_or_none()
	db_session.delete(group_to_graph)
	return group_to_graph


@with_session
def find_layouts(db_session, owner_email=None, is_shared=None, name=None, graph_id=None, limit=None, offset=None,
                 order_by=desc(Layout.updated_at)):
	query = db_session.query(Layout)

	if order_by is not None:
		query = query.order_by(order_by)

	if owner_email is not None:
		query = query.filter(Layout.owner_email.ilike(owner_email))

	if name is not None:
		query = query.filter(Layout.name.ilike(name))

	if graph_id is not None:
		query = query.filter(Layout.graph_id == graph_id)

	if is_shared is not None:
		query = query.filter(Layout.is_shared == is_shared)

	total = query.count()

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()


@with_session
def get_layout_by_id(db_session, layout_id):
	return db_session.query(Layout).filter(Layout.id == layout_id).one_or_none()


@with_session
def add_layout(db_session, owner_email, name, graph_id, is_shared, style_json, positions_json):
	"""

	Parameters
	----------
	db_session - Database session.
	owner_email - ID of user who owns the group
	name - Name of the layout
	graph_id - ID of the graph the layout belongs to.
	is_shared - if layout is shared with groups where graph is shared.
	positions_json - positions_json of the layouts.
	style_json - style_json of the layouts.

	Returns
	-------

	"""
	layout = Layout(owner_email=owner_email, name=name, graph_id=graph_id, is_shared=is_shared, style_json=style_json,
	                positions_json=positions_json)
	db_session.add(layout)
	return layout


@with_session
def update_layout(db_session, id, updated_layout):
	"""

	Parameters
	----------
	db_session: Database session.
	id: Layout ID
	updated_layout: Updated layout data

	Returns
	-------
	Updated Layout Object

	"""
	layout = db_session.query(Layout).filter(Layout.id == id).one_or_none()
	for (key, value) in updated_layout.items():
		setattr(layout, key, value)
	return layout


@with_session
def delete_layout(db_session, id):
	"""
	Delete layout.
	:param db_session: Database session.
	:param id: Unique ID of the layout
	:return: None
	"""
	layout = db_session.query(Layout).filter(Layout.id == id).one_or_none()
	db_session.delete(layout)
	return


@with_session
def find_nodes(db_session, labels=None, names=None, graph_id=None, limit=None, offset=None,
               order_by=desc(Node.updated_at)):
	query = db_session.query(Node)

	if graph_id is not None:
		query = query.filter(Node.graph_id == graph_id)

	names = [] if names is None else names
	labels = [] if labels is None else labels
	if len(names + labels) > 0:
		query = query.filter(
			or_(*([Node.name.ilike(name) for name in names] + [Node.label.ilike(label) for label in labels])))

	total = query.count()

	if order_by is not None:
		query = query.order_by(order_by)

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()


@with_session
def find_edges(db_session, is_directed=None, names=None, edges=None, graph_id=None, limit=None, offset=None,
               order_by=desc(Node.updated_at)):
	query = db_session.query(Edge)

	if graph_id is not None:
		query = query.filter(Edge.graph_id == graph_id)

	if is_directed is not None:
		query = query.filter(Edge.is_directed == is_directed)

	names = [] if names is None else names
	edges = [] if edges is None else edges
	if len(names + edges) > 0:
		names_filter = [Edge.name.ilike(name) for name in names]
		edges_filter = [and_(Edge.head_node_name.ilike(u), Edge.tail_node_name.ilike(v)) for u, v in edges]
		edges_filter.extend([and_(Edge.tail_node_name.ilike(u), Edge.head_node_name.ilike(v)) for u, v in edges])
		edges_filter.extend([and_(Edge.head_node_label.ilike(u), Edge.tail_node_label.ilike(v)) for u, v in edges])
		edges_filter.extend([and_(Edge.tail_node_label.ilike(u), Edge.head_node_label.ilike(v)) for u, v in edges])
		query = query.filter(or_(*(edges_filter + names_filter)))

	total = query.count()

	if order_by is not None:
		query = query.order_by(order_by)

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()
