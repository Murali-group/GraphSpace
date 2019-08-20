from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import joinedload, subqueryload

from applications.users.models import *
from graphspace.wrappers import with_session
from sqlalchemy.orm import defer, undefer, aliased


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
def add_graph(db_session, name, owner_email, is_public=0, default_layout_id=None):
	graph = Graph(name=name, owner_email=owner_email,  is_public=is_public,
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
	version_id = update_graph if 'default_version_id' in updated_graph else graph.default_version_id
	graph_version = db_session.query(GraphVersion).filter(GraphVersion.id == version_id)

	for (key, value) in updated_graph.items():
		if key == 'graph_json' or key == 'style_json':
			setattr(graph_version, key, value)
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
	query = db_session.query(Graph).filter(Graph.id == id)
	query.options(joinedload('graph_versions')).filter(GraphVersion.id==Graph.default_version_id)
	return query.one_or_none()


@with_session
def find_graphs(db_session, owner_email=None, group_ids=None, graph_ids=None, is_public=None, names=None, nodes=None,
				edges=None,
				tags=None, limit=None, offset=None, order_by=desc(Graph.updated_at)):
	query = db_session.query(Graph)
	#query = query.options(defer("graph_json")).options(defer("style_json"))

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
	options_group.append(joinedload('graph_versions'))
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
	query = query.filter(GraphVersion.id==Graph.default_version_id)

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
	layout_to_graph_versions = db_session.query(LayoutToGraphVersion).filter(LayoutToGraphVersion.layout_id == 7).all()
	for obj in layout_to_graph_versions:
		obj.status = "Null"
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


@with_session
def nodes_intersection(db_session, graph_1_id=None, graph_2_id=None):
	"""
		Find node intersection of 2 Graphs.
		:param db_session: Database session.
		:param graph_1_id: Unique ID of Graph 1.
		:param graph_2_id: Unique ID of the Graph 2.
		:return: list: Total, queried nodes
	"""
	alias_node = aliased(Node)
	query = db_session.query(Node, alias_node)

	if graph_1_id is not None and graph_2_id is not None:
		query = query.filter(Node.graph_id == graph_1_id).\
				join(alias_node, Node.name == alias_node.name).\
				filter(alias_node.graph_id == graph_2_id)
	total = query.count()
	return total, query.all()


@with_session
def nodes_difference(db_session, graph_1_id=None, graph_2_id=None):
	"""
		Find node difference of 2 Graphs.
		:param db_session: Database session.
		:param graph_1_id: Unique ID of Graph 1.
		:param graph_2_id: Unique ID of the Graph 2.
		:return: list: Total, queried nodes
	"""
	graph1_query = db_session.query(Node).filter(Node.graph_id == graph_1_id)
	graph2_query = db_session.query(Node).filter(Node.graph_id == graph_2_id)
	sub_q = graph2_query.subquery()

	query = graph1_query.outerjoin(sub_q, sub_q.c.name == Node.name).\
			filter(sub_q.c.name == None)
	total = query.count()
	return total, query.all()


@with_session
def edges_intersection(db_session, graph_1_id=None, graph_2_id=None):
	"""
		Find edge intersection of 2 Graphs.
		:param db_session: Database session.
		:param graph_1_id: Unique ID of Graph 1.
		:param graph_2_id: Unique ID of the Graph 2.
		:return: list: Total, queried nodes
	"""
	alias_edge = aliased(Edge)
	query = db_session.query(Edge, alias_edge)

	if graph_1_id is not None and graph_2_id is not None:
		query = query.filter(Edge.graph_id == graph_1_id).\
				join(alias_edge, Edge.head_node_name == alias_edge.head_node_name).\
				filter(alias_edge.graph_id == graph_2_id).\
				filter(Edge.tail_node_name == alias_edge.tail_node_name)
	total = query.count()
	return total, query.all()


@with_session
def edges_difference(db_session, graph_1_id=None, graph_2_id=None):
	"""
		Find edge difference of 2 Graphs.
		:param db_session: Database session.
		:param graph_1_id: Unique ID of Graph 1.
		:param graph_2_id: Unique ID of the Graph 2.
		:return: list: Total, queried nodes
	"""
	graph1_query = db_session.query(Edge).filter(Edge.graph_id == graph_1_id)
	graph2_query = db_session.query(Edge).filter(Edge.graph_id == graph_2_id)
	sub_q = graph2_query.subquery()

	query = graph1_query.outerjoin(sub_q, sub_q.c.name == Edge.name). \
		filter(sub_q.c.name == None)
	total = query.count()
	return total, query.all()


@with_session
def nodes_subquery(db_session, graph_1_id=None, graph_2_id=None, operation=None):
	"""
		Find node subquery of 2 Graphs.
		:param db_session: Database session.
		:param graph_1_id: Unique ID of Graph 1.
		:param graph_2_id: Unique ID of the Graph 2.
		:param operation: Comparison operation - difference or intersection..
		:return: query.subquery object.
	"""
	alias_node1 = aliased(Node, name='n1')
	alias_node2 = aliased(Node, name='n2')
	if operation == 'intersection':
		query = db_session.query(alias_node1, alias_node2)
		if graph_1_id is not None and graph_2_id is not None:
			query = query.filter(alias_node1.graph_id == graph_1_id). \
				join(alias_node2, alias_node1.name == alias_node2.name). \
				filter(alias_node2.graph_id == graph_2_id)
			n1 = query.subquery(name='s1', with_labels=True)
			db_session.query(Node).filter(Node.graph_id == 6).join(n1, n1.c.name == Node.name)
			return query.subquery(name='s1', with_labels=True)
	else:
		graph1_query = db_session.query(Node).filter(Node.graph_id == graph_1_id)
		graph2_query = db_session.query(Node).filter(Node.graph_id == graph_2_id)
		sub_q = graph2_query.subquery()

		query = graph1_query.outerjoin(sub_q, sub_q.c.name == Node.name). \
			filter(sub_q.c.name == None)
		return query.subquery()

@with_session
def edges_subquery(db_session, graph_1_id=None, graph_2_id=None, operation=None):
	"""
		Find node subquery of 2 Graphs.
		:param db_session: Database session.
		:param graph_1_id: Unique ID of Graph 1.
		:param graph_2_id: Unique ID of the Graph 2.
		:param operation: Comparison operation - difference or intersection..
		:return: query.subquery object.
	"""
	alias_edge = aliased(Edge)
	if operation == 'intersection':
		query = db_session.query(Edge, alias_edge)

		if graph_1_id is not None and graph_2_id is not None:
			query = query.filter(Edge.graph_id == graph_1_id). \
				join(alias_edge, Edge.head_node_name == alias_edge.head_node_name). \
				filter(alias_edge.graph_id == graph_2_id). \
			filter(Edge.tail_node_name == alias_edge.tail_node_name)
			return query.subquery
		else:
			graph1_query = db_session.query(Edge).filter(Edge.graph_id == graph_1_id)
			graph2_query = db_session.query(Edge).filter(Edge.graph_id == graph_2_id)
			sub_q = graph2_query.subquery()

			query = graph1_query.outerjoin(sub_q, sub_q.c.name == Edge.name). \
				filter(sub_q.c.name == None)
			return query.subquery


@with_session
def nodes_intersection_multi(db_session, graphs):
	"""
		Find node intersection of N Graphs.
		:param db_session: Database session.
		:param graph: Unique IDs of the Graphs.
		:return: list: total, queried nodes
	"""
	query = db_session.query(Node).filter(Node.graph_id == graphs[0])
	for graph_id in graphs[1:]:
		sub_q = db_session.query(Node).filter(Node.graph_id == graph_id).subquery()
		query = query.join(sub_q, sub_q.c.name == Node.name)
	total = query.count()
	return total, query.all()


@with_session
def nodes_difference_multi(db_session, graphs):
	"""
		Find node intersection of N Graphs.
		:param db_session: Database session.
		:param graph: Unique IDs of the Graphs.
		:return: list: total, queried nodes
	"""
	query = db_session.query(Node).filter(Node.graph_id == graphs[0])
	for graph_id in graphs[1:]:
		sub_q = db_session.query(Node).filter(Node.graph_id == graph_id).subquery()
		query = query.outerjoin(sub_q, sub_q.c.name == Node.name).\
			filter(sub_q.c.name == None)
	total = query.count()
	return total, query.all()


@with_session
def edges_intersection_multi(db_session, graphs):
	"""
		Find node intersection of N Graphs.
		:param db_session: Database session.
		:param graph: Unique IDs of the Graphs.
		:return: list: total, queried nodes
	"""
	query = db_session.query(Edge).filter(Edge.graph_id == graphs[0])
	for graph_id in graphs[1:]:
		sub_q = db_session.query(Edge).filter(Edge.graph_id == graph_id).subquery()
		query = query.join(sub_q, sub_q.c.head_node_name == Edge.head_node_name)\
			.filter(Edge.tail_node_name == sub_q.c.tail_node_name)
	total = query.count()
	return total, query.all()


@with_session
def edges_difference_multi(db_session, graphs):
	"""
		Find node intersection of N Graphs.
		:param db_session: Database session.
		:param graph: Unique IDs of the Graphs.
		:return: list: total, queried nodes
	"""
	query = db_session.query(Edge).filter(Edge.graph_id == graphs[0])
	for graph_id in graphs[1:]:
		sub_q = db_session.query(Edge).filter(Edge.graph_id == graph_id).subquery()
		query = query.join(sub_q, sub_q.c.head_node_name == Edge.head_node_name)\
			.filter(Edge.tail_node_name == sub_q.c.tail_node_name).filter(sub_q.c.head_node_name == None)
	total = query.count()
	return total, query.all()


@with_session
def nodes_comparison(db_session, comp_expression=None):
	"""
		Work In Progress.
		:param db_session: Database session.
		:param graph: Unique IDs of the Graphs.
		:return: list: total, queried nodes
	"""
	# Infix -> a 'i' ( b - c )
	# Postfix  ->  a b c - 'i'

	comp_expression = [1, 2, 5, 'd', 'i']
	temp_stack = []
	for item in comp_expression:
		if item not in ['d','i']:
			temp_stack.append(item)
		elif item in ['d','i']:
			query1 = temp_stack.pop()
			query2 = temp_stack.pop()
			if type(query1) != int:
				query = db_session.query(Node).filter(Node.graph_id == query2)
				sub_query = query.outerjoin(query1, query1.c.name == Node.name). \
					filter(query1.c.name == None)
			else:
				sub_query = nodes_subquery(db_session, query1, query2, item)
			temp_stack.append(sub_query)
	query = temp_stack.pop()
	count = query.count()

	return count, query.all()


@with_session
def find_graph_versions(db_session, names=None, graph_id=None, limit=None, offset=None,
			   order_by=desc(GraphVersion.updated_at)):
	"""
	Find graph version by Graph ID.
	:param db_session: Database session.
	:param graph_id: Unique ID of the graph
	:param name - Name of the graph version
	:param limit - Number of entities to return. Default value is 20.
	:param offset - Offset the list of returned entities by this number. Default value is 0.
	:param order_by - Defines which column the results will be sorted by.
	:return: Total, Graph Versions
	"""

	query = db_session.query(GraphVersion)

	if graph_id is not None:
		query = query.filter(GraphVersion.graph_id == graph_id)

	names = [] if names is None else names
	if len(names) > 0:
		query = query.filter(
			or_(*([GraphVersion.name.ilike(name) for name in names])))

	total = query.count()

	if order_by is not None:
		query = query.order_by(order_by)

	if offset is not None and limit is not None:
		query = query.limit(limit).offset(offset)

	return total, query.all()

@with_session
def get_graph_version_by_id(db_session, id):
	"""
	Get graph version by ID.
	:param db_session: Database session.
	:param id: Unique ID of the graph version
	:return: Graph Version if id exists else None
	"""
	return db_session.query(GraphVersion).filter(GraphVersion.id == id).one_or_none()

@with_session
def add_graph_version(db_session, graph_id, name, graph_json, owner_email, style_json=None, description=None, is_default=None):
	"""
	Get graph version by ID.
	:param db_session: Database session.
	:param graph_id: Unique ID of the graph
	:param name - Name of the graph version
	:param graph_json - positions_json of the layouts.
	:param owner_email - ID of user who owns the graph
	:param style_json - style_json of the layouts.
	:param description - ID of the graph the layout belongs to.
	:param is_default - Set this graph_version as the default version of the graph
	:return: Graph Version if id exists else None
	"""
	graph_version = GraphVersion(name=name, graph_id=graph_id, graph_json=graph_json, style_json=style_json, owner_email=owner_email, description=description)
	if is_default is not None:
		set_default_version(db_session, graph_id, graph_version.id)
	db_session.add(graph_version)
	return graph_version

@with_session
def delete_graph_version(db_session, id):
	"""
	Delete graph version.
	:param db_session: Database session.
	:param id: Unique ID of the graph version
	:return: None
	"""
	graph_version = db_session.query(GraphVersion).filter(GraphVersion.id == id).one_or_none()
	db_session.delete(graph_version)
	return

@with_session
def set_default_version(db_session, graph_id, default_version_id):
	"""
	Set the default graph version.
	:param db_session: Database session.
	:param graph_id: Unique ID of the graph
	:param default_version_id: Unique ID of the graph version
	:return: None
	"""
	graph = db_session.query(Graph).filter(Graph.id == graph_id).one_or_none()
	setattr(graph, 'default_version_id', default_version_id)
	return


@with_session
def get_graph_version_to_layout_status(db_session, graph_version_id, layout_id):
	"""
	GET graph version to layout compatibility status.
	:param db_session: Database session.
	:param graph_version_id: Unique ID of the graph version
	:param layout_id: Unique ID of the layout
	:return: Graph Version to Layout compatibility status if it exists else None
	"""
	return db_session.query(LayoutToGraphVersion).filter(and_(LayoutToGraphVersion.graph_version_id == graph_version_id, LayoutToGraphVersion.layout_id == layout_id)).one_or_none()


@with_session
def add_graph_version_to_layout_status(db_session, graph_version_id, layout_id, status=None):
	"""
	ADD graph version to layout compatibility.
	:param db_session: Database session.
	:param graph_version_id: Unique ID of the graph version
	:param layout_id - Unique ID of the layout.
	:param status - Compatibility status. [Default = None].
	:return: Graph Version to Layout compatibility status if it exists else None
	"""
	graph_version_to_layout = LayoutToGraphVersion(graph_version_id=graph_version_id, layout_id=layout_id, status=status)
	db_session.add(graph_version_to_layout)
	return graph_version_to_layout


@with_session
def delete_graph_version_to_layout_status(db_session, graph_version_id, layout_id):
	"""
	DELETE graph version.
	:param db_session: Database session.
	:param id: Unique ID of the graph version
	:return: None
	"""
	graph_version_to_layout = db_session.query(LayoutToGraphVersion).filter(and_(LayoutToGraphVersion.graph_version_id == graph_version_id,
																		 LayoutToGraphVersion.layout_id == layout_id)).one_or_none()
	db_session.delete(graph_version_to_layout)
	return


@with_session
def update_graph_version_to_layout_status(db_session, graph_version_id, layout_id=None, status=None):
	"""
	UPDATE graph version to layout compatibility.
	:param db_session: Database session.
	:param graph_version_id: Unique ID of the graph version
	:param layout_id - Unique ID of the layout.
	:param status - Compatibility status. [Default = None].
	:return: Graph Version to Layout compatibility status if layout_id is passed and row exists else None
	"""

	query = db_session.query(LayoutToGraphVersion).filter(LayoutToGraphVersion.graph_version_id == graph_version_id)
	if layout_id:
		query = query.filter(LayoutToGraphVersion.layout_id == layout_id)

	graph_version_to_layout = query.all()

	for item in graph_version_to_layout:
		item.status = status
	# if len(graph_version_to_layout) >1:
	#	return {"message": "Updated status of %d Layouts" % (len(graph_version_to_layout))}
	return graph_version_to_layout[0]
