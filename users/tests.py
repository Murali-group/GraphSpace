from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy.orm import sessionmaker

from django.test import TestCase
from graphspace.database import Database
from users.models import *

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



