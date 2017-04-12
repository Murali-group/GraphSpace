from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from applications.users.models import *
from django.test import TestCase
from graphspace.database import Database

Session = sessionmaker()


class UserModelTestCase(TestCase):
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
		self.session.add(User(email='user1@example.com', password="password", is_admin=0))
		self.session.commit()
		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.assertEqual(user1.email, 'user1@example.com')
		self.assertEqual(user1.password, 'password')

		# Update
		user1.password = 'updated_password'
		self.session.commit()
		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.assertEqual(user1.password, 'updated_password')

		# Delete
		self.session.delete(user1)
		self.session.commit()
		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.assertIsNone(user1)

		# Retrieve
		num_users = self.session.query(User).count()
		self.assertEqual(num_users, 0)

	def test_password_reset_codes_relationship(self):
		self.session.add(User(email='user1@example.com', password="password", is_admin=0))
		self.session.add(PasswordResetCode(email='user1@example.com', code="code1"))
		self.session.add(PasswordResetCode(email='user1@example.com', code="code2"))
		self.session.commit()

		num_password_resetcodes = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').count()
		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.assertEqual(len(user1.password_reset_codes), 2)

	def test_owned_groups_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		self.session.add(Group(name="group2", owner_email='owner@example.com', description="description"))
		self.session.commit()

		num_owned_groups = self.session.query(Group).filter(Group.owner_email == 'owner@example.com').count()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertEqual(len(owner.owned_groups), num_owned_groups)

	def test_owned_layouts_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))
		graph1 = self.session.query(Graph).filter(Graph.owner_email == 'owner@example.com').one_or_none()
		self.session.add(Layout(graph_id=graph1.id, name='layout1', owner_email='owner@example.com', json='{}', is_shared=0, original_json='{}'))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		layout1 = self.session.query(Layout).filter(Layout.name == 'layout1').one_or_none()

		self.assertEqual(owner.owned_layouts[0].id, layout1.id)

	def test_member_groups_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		self.session.add(Group(name="group2", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()
		group2 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group2')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		self.session.add(GroupToUser(user_id=member.id, group_id=group2.id))
		self.session.commit()

		num_member_groups = self.session.query(GroupToUser).filter(GroupToUser.user_id == member.id).count()
		self.assertEqual(len(member.member_groups), num_member_groups)


class PasswordResetCodeModelTestCase(TestCase):

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
		self.session.add(User(email='user1@example.com', password="password", is_admin=0))
		self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').one_or_none()
		self.assertEqual(password_resetcode1.email, 'user1@example.com')
		self.assertEqual(password_resetcode1.code, 'code')
		self.session.commit()

		# Update
		password_resetcode1.code = 'code2'
		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').one_or_none()
		self.assertEqual(password_resetcode1.code, 'code2')
		self.session.commit()

		# Delete
		self.session.delete(password_resetcode1)
		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').one_or_none()
		self.assertIsNone(password_resetcode1)
		self.session.commit()

		# Retrieve
		num_password_resetcodes = self.session.query(PasswordResetCode).count()
		self.assertEqual(num_password_resetcodes, 0)


	def test_email_fkey_constraint(self):
		"""
		Email column should satisfy foreign key constraint.
		"""

		with self.assertRaises(IntegrityError):
			self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
			self.session.commit()


	def test_email_uc_constraint(self):
		"""
		Email column and code should satisfy Unique constraint.
		"""
		with self.assertRaises(IntegrityError):
			self.session.add(User(email='user1@example.com', password="password", is_admin=0))
			self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
			self.session.commit()
			self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in password_reset_code table should also be deleted
		"""
		self.session.add(User(email='user1@example.com', password="password", is_admin=0))
		self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
		self.session.commit()

		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.session.delete(user1)
		self.session.commit()
		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.assertIsNone(user1)

		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').one_or_none()
		self.assertIsNone(password_resetcode1)
		self.session.commit()

	def test_cascade_on_user_update(self):
		"""
		On updating user row, the corresponding row in password_reset_code table should also be updated
		"""
		self.session.add(User(email='user1@example.com', password="password", is_admin=0))
		self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
		self.session.commit()
		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').one_or_none()

		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		user1.email = 'user2@example.com'
		self.session.commit()

		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.id == password_resetcode1.id).one_or_none()
		self.assertEqual(password_resetcode1.email, 'user2@example.com')
		self.session.commit()

	def test_user_relationship(self):
		self.session.add(User(email='user1@example.com', password="password", is_admin=0))
		self.session.add(PasswordResetCode(email='user1@example.com', code="code"))
		self.session.commit()

		password_resetcode1 = self.session.query(PasswordResetCode).filter(
			PasswordResetCode.email == 'user1@example.com').one_or_none()
		user1 = self.session.query(User).filter(User.email == 'user1@example.com').one_or_none()
		self.assertEqual(password_resetcode1.user.id, user1.id)


class GroupModelTestCase(TestCase):

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
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()
		self.assertEqual(group1.owner_email, 'owner@example.com')
		self.assertEqual(group1.description, 'description')
		self.assertEqual(group1.name, 'group1')
		self.session.commit()

		# Update
		group1.name = 'updated_group1'
		group1 = self.session.query(Group).filter(Group.id == group1.id).one_or_none()
		self.assertEqual(group1.owner_email, 'owner@example.com')
		self.assertEqual(group1.description, 'description')
		self.assertEqual(group1.name, 'updated_group1')
		self.session.commit()

		# Delete
		self.session.delete(group1)
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()
		self.assertIsNone(group1)
		self.session.commit()

		# Retrieve
		num_groups = self.session.query(Group).count()
		self.assertEqual(num_groups, 0)

	def test_owner_email_fkey_constraint(self):
		"""
		Owner Email column should satisfy foreign key constraint.
		"""

		with self.assertRaises(IntegrityError):
			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			self.session.commit()


	def test_name_owner_email_uc_constraint(self):
		"""
		Owner Email column and Name column should satisfy Unique constraint.
		"""
		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			self.session.commit()
			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in group table should also be deleted
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		self.session.commit()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.session.delete(owner)
		self.session.commit()
		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.assertIsNone(owner)

		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()
		self.assertIsNone(group1)
		self.session.commit()


	def test_cascade_on_user_update(self):
		"""
		On deleting user row, the corresponding row in group table should also be deleted
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		self.session.commit()
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		owner.email = 'owner_updated@example.com'
		self.session.commit()

		group1 = self.session.query(Group).filter(Group.id == group1.id).one_or_none()
		self.assertEqual(group1.owner_email, 'owner_updated@example.com')
		self.session.commit()

	def test_owner_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		self.session.commit()

		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()

		self.assertEqual(group1.owner.id, owner.id)

	def test_owned_graphs_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(Graph(name='graph1', owner_email='owner@example.com', json='{}', is_public=0))


		graph1 = self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph1')).one_or_none()

		self.session.add(Graph(name='graph2', owner_email='owner@example.com', json='{}', is_public=0))


		graph2 = self.session.query(Graph).filter(and_(Graph.owner_email == 'owner@example.com', Graph.name == 'graph2')).one_or_none()

		owner = self.session.query(User).filter(User.email == 'owner@example.com').one_or_none()
		self.session.commit()
		self.assertEqual(len(owner.owned_graphs), 2)


	def test_members_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(User(email='member1@example.com', password="password", is_admin=0))
		member1 = self.session.query(User).filter(User.email == 'member1@example.com').one_or_none()
		self.session.add(User(email='member2@example.com', password="password", is_admin=0))
		member2 = self.session.query(User).filter(User.email == 'member2@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member1.id, group_id=group1.id))
		self.session.add(GroupToUser(user_id=member2.id, group_id=group1.id))
		self.session.commit()

		self.assertEqual(len(group1.members), 2)


class GroupToUserModelTestCase(TestCase):

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

		self.assertEqual(group2user1.user_id, member.id)
		self.assertEqual(group2user1.group_id, group1.id)
		self.session.commit()

		# Delete
		self.session.delete(group2user1)
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()
		self.assertIsNone(group2user1)
		self.session.commit()

	def test_user_id_fkey_constraint(self):
		"""
		User ID column should satisfy foreign key constraint.
		"""

		with self.assertRaises(IntegrityError):
			self.session.add(GroupToUser(user_id=1, group_id=2))
			self.session.commit()

	def test_user_id_group_id_unique_constraint(self):
		"""
		Composite key User Id, Group ID should be unique.
		"""
		with self.assertRaises(IntegrityError):
			self.session.add(User(email='owner@example.com', password="password", is_admin=0))
			self.session.add(User(email='member@example.com', password="password", is_admin=0))
			member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()
			self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
			group1 = self.session.query(Group).filter(and_(
				Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

			self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
			self.session.commit()
			self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
			self.session.commit()

	def test_cascade_on_user_delete(self):
		"""
		On deleting user row, the corresponding row in group table should also be deleted
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		member_id = member.id
		group_id = group1.id
		self.session.commit()

		self.session.delete(member)
		self.session.commit()
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()
		self.assertIsNone(member)

		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member_id, GroupToUser.group_id == group_id)).one_or_none()
		self.assertIsNone(group2user1)
		self.session.commit()


	def test_cascade_on_user_update(self):
		"""
		On deleting user row, the corresponding row in group table should also be deleted
		"""
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))
		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()
		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()
		self.session.commit()

		old_member_id = member.id
		member.id = 2
		self.session.commit()
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == old_member_id, GroupToUser.group_id == group1.id)).one_or_none()
		self.assertIsNone(group2user1)

		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == 2, GroupToUser.group_id == group1.id)).one_or_none()
		self.assertIsNotNone(group2user1)

	def test_user_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.commit()

		self.assertEqual(group2user1.user.id, member.id)

	def test_group_relationship(self):
		self.session.add(User(email='owner@example.com', password="password", is_admin=0))

		self.session.add(User(email='member@example.com', password="password", is_admin=0))
		member = self.session.query(User).filter(User.email == 'member@example.com').one_or_none()

		self.session.add(Group(name="group1", owner_email='owner@example.com', description="description"))
		group1 = self.session.query(Group).filter(and_(
			Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

		self.session.add(GroupToUser(user_id=member.id, group_id=group1.id))
		group2user1 = self.session.query(GroupToUser).filter(and_(GroupToUser.user_id == member.id, GroupToUser.group_id == group1.id)).one_or_none()

		self.session.commit()

		self.assertEqual(group2user1.group.id, group1.id)

	def test_graphs_relationship(self):
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

		self.assertEqual(group1.graphs[0].id, graph1.id)






