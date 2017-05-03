from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload
from applications.graphs.models import *
from applications.users.models import *
from django.test import TestCase
from graphspace.database import Database

Session = sessionmaker()


class GraphModelTestCase(TestCase):
	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_crud_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""

		# Create
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertEqual(graph1.name, 'graph1')
		#
		# Update
		graph1.name = 'updated_graph'
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertEqual(graph1.name, 'updated_graph')
		#
		# Delete
		self.session.delete(graph1)
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(graph1)

		# Retrieve
		num_graphs = self.session.query(Graph).count()
		self.assertEqual(num_graphs, 0)

	def test_owner_email_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			self.session.commit()

	def test_default_layout_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0, default_layout_id=1))
			self.session.commit()

	def test_name_owner_email_uc_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			self.session.commit()
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=1))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in graph table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.session.delete(owner)
		self.session.commit()
		self.assertIsNone(self.session.query(User).filter(User.email == 'owner@example.com').one_or_none())

		self.assertIsNone(self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph1')).one_or_none())
		self.session.commit()

	def test_cascade_on_user_update(self):
		"""
		On deleting user row, the corresponding row in graph table should also be updated
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		self.session.commit()
		graph1 = self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph1')).one_or_none()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		owner.email = 'owner_updated@example.com'
		self.session.commit()

		graph1 = self.session.query(Graph).filter(Graph.id == graph1.id).one_or_none()
		self.assertEqual(graph1.owner_email, 'owner_updated@example.com')
		self.session.commit()

	def test_owner_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		self.session.commit()

		graph1 = self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph1')).one_or_none()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.assertEqual(graph1.owner.id, owner.id)

	def test_nodes_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source1'))
		self.session.commit()

		graph1 = self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph1')).one_or_none()
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()

		self.assertEqual(graph1.nodes[0].id, source.id)

		graph1 = self.session.query(Graph).options(joinedload('nodes')).filter(Graph.nodes.any(Node.label.like('source1'))).one_or_none()
		self.assertEqual(graph1.name, 'graph1')

	def test_edges_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.session.commit()
		self.assertEqual(graph1.edges[0].id, edge1.id)


	def test_layouts_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()

		self.assertEqual(graph1.layouts[0].id, layout1.id)

	def test_default_layout_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()
		self.assertIsNone(graph1.default_layout)

		graph1.default_layout_id = layout1.id
		self.session.commit()

		self.assertEqual(graph1.default_layout.id, layout1.id)

	def test_groups_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()

		self.assertEqual(graph1.groups[0].id, group1.id)

	def test_tags_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
		self.assertEqual(graph1.tags[0].id, tag1.id)


class NodeModelTestCase(TestCase):
	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_crud_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""

		# Create
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		self.session.commit()
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()

		self.assertEqual(source.label, 'source')
		self.assertEqual(target.label, 'target')
		#
		# Update
		source.label = 'updated_source'
		self.session.commit()
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		self.assertEqual(source.label, 'updated_source')
		#
		# Delete
		self.session.delete(source)
		self.session.commit()
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		self.assertIsNone(source)

		# Retrieve
		num_nodes = self.session.query(Node).count()
		self.assertEqual(num_nodes, 1)

	def test_graph_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(Node(graph_id=1, name='source', label='source'))
			self.session.commit()

	def test_graph_id_name_uc_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(Node(graph_id=graph1.id, name='source', label='source1'))
			self.session.add(Node(graph_id=graph1.id, name='source', label='source2'))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in node table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source1'))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.session.delete(owner)
		self.session.commit()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertIsNone(owner)

		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		self.assertIsNone(source)

	def test_cascade_on_graph_delete(self):
		"""
		On deleting graph row, the corresponding row in node table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source1'))
		self.session.commit()

		self.session.delete(graph1)
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(graph1)

		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		self.assertIsNone(source)

	def test_graph_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source1'))
		self.session.commit()

		graph1 = self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph1')).one_or_none()
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()

		self.assertEqual(source.graph.id, graph1.id)

	def test_source_edges_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()

		self.assertEqual(source.source_edges[0].id, edge1.id)
		self.assertEqual(len(target.source_edges), 0)

	def test_target_edges_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()

		self.assertEqual(target.target_edges[0].id, edge1.id)
		self.assertEqual(len(source.target_edges), 0)


class EdgeModelTestCase(TestCase):
	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_crud_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""

		# Create
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()
		edge1 = self.session.query(Edge).filter(Edge.graph_id == graph1.id).one_or_none()
		self.assertEqual(edge1.name, 'edge1')

		# Update
		edge1.name = 'updated_edge1'
		self.session.commit()
		edge1 = self.session.query(Edge).filter(Edge.graph_id == graph1.id).one_or_none()
		self.assertEqual(edge1.name, 'updated_edge1')

		# Delete
		self.session.delete(edge1)
		self.session.commit()
		edge1 = self.session.query(Edge).filter(Edge.graph_id == graph1.id).one_or_none()
		self.assertIsNone(edge1)

		# Retrieve
		num_edges = self.session.query(Edge).count()
		self.assertEqual(num_edges, 0)

	def test_graph_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
			self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
			source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
			target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
			self.session.delete(graph1)
			self.session.commit()

			self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
			self.session.commit()

	def test_head_node_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
			self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
			source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
			target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
			self.session.delete(source)
			self.session.commit()

			self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
			self.session.commit()

	def test_tail_node_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
			self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
			source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
			target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
			self.session.delete(target)
			self.session.commit()

			self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
			self.session.commit()

	def test_graph_id_name_uc_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
			self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
			source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
			target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
			self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
			self.session.add(Edge(graph_id=graph1.id, head_node_id=target.id, tail_node_id=source.id, is_directed=1, name='edge1'))
			self.session.commit()

	def test_graph_id_head_node_id_tail_node_id_uc_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
			self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
			source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
			target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
			self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
			self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge2'))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in edge table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.session.delete(owner)
		self.session.commit()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertIsNone(owner)

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.assertIsNone(edge1)

	def test_cascade_on_graph_delete(self):
		"""
		On deleting graph row, the corresponding row in edge table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		self.session.delete(graph1)
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(graph1)

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.assertIsNone(edge1)

	def test_cascade_on_node_delete(self):
		"""
		On deleting node row, the corresponding row in edge table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		self.session.delete(source)
		self.session.commit()
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		self.assertIsNone(source)

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.assertIsNone(edge1)

	def test_graph_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.assertEqual(edge1.graph.id, graph1.id)

	def test_head_node_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.assertEqual(edge1.head_node.id, source.id)

		edge1 = self.session.query(Edge).options(joinedload('head_node')).filter(Edge.head_node.has(Node.label.like('source'))).one_or_none()
		self.assertEqual(edge1.name, 'edge1')

	def test_tail_node_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Node(graph_id=graph1.id, name='source', label='source'))
		self.session.add(Node(graph_id=graph1.id, name='target', label='target'))
		source = self.session.query(Node).filter(Node.name == 'source').one_or_none()
		target = self.session.query(Node).filter(Node.name == 'target').one_or_none()
		self.session.add(Edge(graph_id=graph1.id, head_node_id=source.id, tail_node_id=target.id, is_directed=1, name='edge1'))
		self.session.commit()

		edge1 = self.session.query(Edge).filter(Edge.name == 'edge1').one_or_none()
		self.assertEqual(edge1.tail_node.id, target.id)


class GroupToGraphModelTestCase(TestCase):

	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_add_delete_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""
		# Create
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()

		self.assertEqual(group2graph1.graph_id, graph1.id)
		self.assertEqual(group2graph1.group_id, group1.id)
		self.session.commit()

		# Delete
		self.session.delete(group2graph1)
		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()
		self.assertIsNone(group2graph1)
		self.session.commit()

	def test_graph_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

			self.session.add(User(email='member@example.com', password="password", is_admin=0))
			member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			group1 = self.session.query(Group).filter(and_(
				Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

			self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
			group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.delete(graph1)
			self.session.commit()

			self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
			self.session.commit()

	def test_group_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

			self.session.add(User(email='member@example.com', password="password", is_admin=0))
			member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			group1 = self.session.query(Group).filter(and_(
				Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

			self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
			group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.delete(group1)
			self.session.commit()

			self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
			self.session.commit()

	def test_graph_id_group_id_unique_constraint(self):
		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

			self.session.add(User(email='member@example.com', password="password", is_admin=0))
			member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			group1 = self.session.query(Group).filter(and_(
				Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

			self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
			group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
			self.session.commit()
			self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
			self.session.commit()

	def test_cascade_on_group_member_delete(self):

		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()

		graph_id = graph1.id
		group_id = group1.id
		self.session.commit()

		self.session.delete(member)
		self.session.commit()
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()
		self.assertIsNone(member)

		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()
		self.assertIsNotNone(group2graph1)
		self.session.commit()

	def test_cascade_on_group_owner_delete(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.add(Graph(name='graph1', owner_email='member@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'member@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()

		self.session.delete(owner)
		self.session.commit()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertIsNone(owner)

		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()
		self.assertIsNone(group2graph1)
		self.session.commit()

	def test_cascade_on_graph_owner_delete(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(User(email='graph_owner@example.com', password="password", is_admin=0))
		graph_owner = self.session.query(User).filter(User.email == 'graph_owner@example.com').one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		self.session.add(GroupToUser(user_id=graph_owner.id, group_id=group1.id))

		self.session.add(Graph(name='graph1', owner_email='graph_owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'graph_owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()

		self.session.delete(graph_owner)
		self.session.commit()
		graph_owner = self.session.query(User).filter(User.email == 'graph_owner@example.com').one_or_none()
		self.assertIsNone(graph_owner)

		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()
		self.assertIsNone(group2graph1)
		self.session.commit()

	def test_cascade_on_graph_delete(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()

		graph_id = graph1.id
		self.session.delete(graph1)
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(graph1)

		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph_id, GroupToGraph.group_id == group1.id)).one_or_none()
		self.assertIsNone(group2graph1)
		self.session.commit()

	def test_cascade_on_group_delete(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()

		group_id = group1.id
		self.session.delete(group1)
		self.session.commit()
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()
		self.assertIsNone(group1)

		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group_id)).one_or_none()
		self.assertIsNone(group2graph1)
		self.session.commit()

	def test_graph_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()
		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()

		self.assertEqual(group2graph1.graph_id, graph1.id)

	def test_group_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(GroupToGraph(graph_id=graph1.id, group_id=group1.id))
		self.session.commit()
		group2graph1 = self.session.query(GroupToGraph).filter(and_(GroupToGraph.graph_id == graph1.id, GroupToGraph.group_id == group1.id)).one_or_none()

		self.assertEqual(group2graph1.group_id, group1.id)


class GraphTagModelTestCase(TestCase):
	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_crud_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""

		# Create
		self.session.add(GraphTag(name='tag1'))
		self.session.commit()

		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.assertEqual(tag1.name, 'tag1')

		# Update
		tag1.name = 'updated_tag1'
		self.session.commit()
		tag1 = self.session.query(GraphTag).filter(GraphTag.id == tag1.id).one_or_none()
		self.assertEqual(tag1.name, 'updated_tag1')

		# Delete
		self.session.delete(tag1)
		self.session.commit()
		tag1 = self.session.query(GraphTag).filter(GraphTag.id == tag1.id).one_or_none()
		self.assertIsNone(tag1)

		# Retrieve
		num_tags = self.session.query(GraphTag).count()
		self.assertEqual(num_tags, 0)

	def test_name_uc_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(GraphTag(name='tag1'))
			self.session.add(GraphTag(name='tag1'))
			self.session.commit()

	def test_graphs_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
		self.assertEqual(tag1.graphs[0].id, graph1.id)


class GraphToTagModelTestCase(TestCase):

	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_add_delete_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""
		# Create
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph1.id, GraphToTag.tag_id == tag1.id)).one_or_none()

		self.assertEqual(graph2tag1.graph_id, graph1.id)
		self.assertEqual(graph2tag1.tag_id, tag1.id)
		self.session.commit()

		# Delete
		self.session.delete(graph2tag1)
		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph1.id, GraphToTag.tag_id == tag1.id)).one_or_none()
		self.assertIsNone(graph2tag1)
		self.session.commit()

	def test_graph_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))

			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

			self.session.add(GraphTag(name='tag1'))
			tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

			self.session.delete(graph1)
			self.session.commit()

			self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
			self.session.commit()


	def test_tag_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))

			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

			self.session.add(GraphTag(name='tag1'))
			tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

			self.session.delete(tag1)
			self.session.commit()

			self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
			self.session.commit()

	def test_graph_id_tag_id_unique_constraint(self):
		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))

			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

			self.session.add(GraphTag(name='tag1'))
			tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

			self.session.delete(tag1)
			self.session.commit()

			self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
			self.session.commit()

			self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
			self.session.commit()

	def test_cascade_on_graph_delete(self):

		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))

		graph_id = graph1.id
		tag_id = tag1.id
		self.session.commit()

		self.session.delete(graph1)
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(graph1)

		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph_id, GraphToTag.tag_id == tag_id)).one_or_none()
		self.assertIsNone(graph2tag1)
		self.session.commit()

	def test_cascade_on_tag_delete(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))

		graph_id = graph1.id
		tag_id = tag1.id
		self.session.commit()

		self.session.delete(tag1)
		self.session.commit()
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()
		self.assertIsNone(tag1)

		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph_id, GraphToTag.tag_id == tag_id)).one_or_none()
		self.assertIsNone(graph2tag1)
		self.session.commit()

	def test_cascade_on_graph_owner_delete(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))

		graph_id = graph1.id
		tag_id = tag1.id
		self.session.commit()

		self.session.delete(owner)
		self.session.commit()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertIsNone(owner)

		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph_id, GraphToTag.tag_id == tag_id)).one_or_none()
		self.assertIsNone(graph2tag1)
		self.session.commit()

	def test_graph_relationship(self):

		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph1.id, GraphToTag.tag_id == tag1.id)).one_or_none()

		self.assertEqual(graph2tag1.graph.id, graph1.id)

	def test_tag_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()

		self.session.add(GraphTag(name='tag1'))
		tag1 = self.session.query(GraphTag).filter(GraphTag.name == 'tag1').one_or_none()

		self.session.add(GraphToTag(graph_id=graph1.id, tag_id=tag1.id))
		graph2tag1 = self.session.query(GraphToTag).filter(and_(GraphToTag.graph_id == graph1.id, GraphToTag.tag_id == tag1.id)).one_or_none()

		self.assertEqual(graph2tag1.tag.id, tag1.id)


class LayoutModelTestCase(TestCase):
	def setUp(self):
		db = Database()
		# connect to the database
		self.connection = db.engine.connect()
		# begin a non-ORM transaction
		self.trans = self.connection.begin()
		# bind an individual Session to the connection
		self.session = Session(bind=self.connection)

	def tearDown(self):
		self.session.close()

		# rollback - everything that happened with the
		# Session above (including calls to commit())
		# is rolled back.
		self.trans.rollback()

		# return connection to the Engine
		self.connection.close()

	def test_crud_operation(self):
		"""
		Basic CRUD (Create, Retrieve, Update, Delete) operation should work properly.
		"""

		# Create
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()
		layout1 = self.session.query(Layout).filter(Layout.owner_email == 'owner@example.com').one_or_none()

		self.assertEqual(layout1.name, 'layout1')

		# Update
		layout1.name = 'updated_layout1'
		self.session.commit()
		layout1 = self.session.query(Layout).filter(Layout.owner_email == 'owner@example.com').one_or_none()
		self.assertEqual(layout1.name, 'updated_layout1')
		#
		# Delete
		self.session.delete(layout1)
		self.session.commit()
		layout1 = self.session.query(Layout).filter(Layout.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(layout1)

		# Retrieve
		num_layouts = self.session.query(Layout).count()
		self.assertEqual(num_layouts, 0)

	def test_graph_id_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.delete(graph1)
			self.session.commit()

			self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
			self.session.commit()

	def test_owner_email_fkey_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
			self.session.delete(owner)
			self.session.commit()

			self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
			self.session.commit()

	def test_name_graph_id_owner_email_uc_constraint(self):

		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
			graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
			self.session.commit()

			self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
			self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{"a": "a"}', is_public=1, is_shared=1, original_json='{"a": "a"}'))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in node table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.session.delete(owner)
		self.session.commit()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertIsNone(owner)

		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()
		self.assertIsNone(layout1)

	def test_cascade_on_graph_delete(self):
		"""
		On deleting graph row, the corresponding row in node table should also be deleted.
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		self.session.delete(graph1)
		self.session.commit()
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.assertIsNone(graph1)

		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()
		self.assertIsNone(layout1)

	def test_graph_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()

		self.assertEqual(layout1.graph.id, graph1.id)

	def test_owner_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()

		self.assertEqual(layout1.owner.id, owner.id)

	def test_default_layout_graph_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_public=0, is_shared=0, original_json='{}'))
		self.session.commit()

		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()
		self.assertIsNone(layout1.default_layout_graph)

		graph1.default_layout_id = layout1.id
		self.session.commit()

		self.assertEqual(layout1.default_layout_graph.id, graph1.id)











