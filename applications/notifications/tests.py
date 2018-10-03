from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, joinedload
from applications.notifications.models import *
from applications.users.models import *
from django.test import TestCase
from graphspace.database import Database

Session = sessionmaker()


class OwnerNotificationModelTestCase(TestCase):

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
        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))
        self.session.add(OwnerNotification(
            owner_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            is_read=False,
            type='update'))

        self.session.commit()
        notification1 = self.session.query(OwnerNotification).filter(
            OwnerNotification.owner_email == 'owner@example.com').one_or_none()
        self.assertEqual(notification1.message, 'testing')

        # Update
        notification1.message = 'updated_notification'
        self.session.commit()
        notification1 = self.session.query(OwnerNotification).filter(
            OwnerNotification.owner_email == 'owner@example.com').one_or_none()
        self.assertEqual(notification1.message, 'updated_notification')

        # Delete
        self.session.delete(notification1)
        self.session.commit()
        notification1 = self.session.query(OwnerNotification).filter(
            OwnerNotification.owner_email == 'owner@example.com').one_or_none()
        self.assertIsNone(notification1)

        # Retrieve
        num_notifications = self.session.query(OwnerNotification).count()
        self.assertEqual(num_notifications, 0)

    def test_owner_email_fkey_constraint(self):

        with self.assertRaises(IntegrityError):
            self.session.add(OwnerNotification(
                owner_email='owner@example.com',
                message="testing",
                resource="graph",
                resource_id=1,
                is_read=False,
                type='update'))
            self.session.commit()

    def test_cascade_on_user_delete(self):
        """
        On deleting user row, the corresponding row in OwnerNotification table should also be deleted.
        """
        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))
        self.session.add(OwnerNotification(
            owner_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            is_read=False,
            type='update'))

        self.session.commit()

        owner = self.session.query(User).filter(
            User.email == 'owner@example.com').one_or_none()
        self.session.delete(owner)
        self.session.commit()
        self.assertIsNone(self.session.query(User).filter(
            User.email == 'owner@example.com').one_or_none())

        self.assertIsNone(self.session.query(OwnerNotification).filter(and_(
            OwnerNotification.owner_email == 'owner@example.com', OwnerNotification.message == 'testing')).one_or_none())
        self.session.commit()

    def test_cascade_on_user_update(self):
        """
        On updating user row, the corresponding row in OwnerNotification table should also be updated
        """
        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))

        self.session.add(OwnerNotification(
            owner_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            is_read=False,
            type='update'))

        self.session.commit()
        notification1 = self.session.query(OwnerNotification).filter(and_(
            OwnerNotification.owner_email == 'owner@example.com', OwnerNotification.message == 'testing')).one_or_none()

        owner = self.session.query(User).filter(
            User.email == 'owner@example.com').one_or_none()
        owner.email = 'owner_updated@example.com'
        self.session.commit()

        notification1 = self.session.query(OwnerNotification).filter(
            OwnerNotification.id == notification1.id).one_or_none()
        self.assertEqual(notification1.owner_email,
                         'owner_updated@example.com')
        self.session.commit()

    def test_owner_relationship(self):
        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))

        self.session.add(OwnerNotification(
            owner_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            is_read=False,
            type='update'))

        self.session.commit()

        notification1 = self.session.query(OwnerNotification).filter(and_(
            OwnerNotification.owner_email == 'owner@example.com', OwnerNotification.message == 'testing')).one_or_none()
        owner = self.session.query(User).filter(
            User.email == 'owner@example.com').one_or_none()

        self.assertEqual(notification1.owner.id, owner.id)


class GroupNotificationModelTestCase(TestCase):

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
        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))
        self.session.add(
            Group(name="group1", owner_email='owner@example.com', description="description", invite_code="test"))
        group1 = self.session.query(Group).filter(and_(Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()
        self.session.add(GroupNotification(
            owner_email='owner@example.com',
            member_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            group_id=group1.id,
            is_read=False,
            type='share'))

        self.session.commit()
        notification1 = self.session.query(GroupNotification).filter(
            GroupNotification.group_id == group1.id).one_or_none()
        self.assertEqual(notification1.message, 'testing')

        # Update
        notification1.message = 'updated_notification'
        self.session.commit()
        notification1 = self.session.query(GroupNotification).filter(
            GroupNotification.group_id == group1.id).one_or_none()
        self.assertEqual(notification1.message, 'updated_notification')

        # Delete
        self.session.delete(notification1)
        self.session.commit()
        notification1 = self.session.query(GroupNotification).filter(
            GroupNotification.group_id == group1.id).one_or_none()
        self.assertIsNone(notification1)

        # Retrieve
        num_notifications = self.session.query(GroupNotification).count()
        self.assertEqual(num_notifications, 0)

    def test_group_id_fkey_constraint(self):

        with self.assertRaises(IntegrityError):
            self.session.add(GroupNotification(
                owner_email='owner@example.com',
                member_email='owner@example.com',
                message="testing",
                resource="graph",
                resource_id=1,
                group_id=1,
                is_read=False,
                type='share'))
            self.session.commit()

    def test_owner_relationship(self):

        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))
        self.session.add(
            Group(name="group1", owner_email='owner@example.com', description="description", invite_code="test"))
        self.session.commit()

        group1 = self.session.query(Group).filter(and_(
            Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

        self.session.add(GroupNotification(
            owner_email='owner@example.com',
            member_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            group_id=group1.id,
            is_read=False,
            type='share'))

        group_notification1 = self.session.query(GroupNotification).filter(
            GroupNotification.message == 'testing').one_or_none()

        self.assertEqual(group_notification1.group.id, group1.id)

    def test_cascade_on_group_delete(self):
        """
        On deleting group row, the corresponding row in GroupNotification table should also be deleted.
        """
        self.session.add(User(email='owner@example.com',
                              password="password", is_admin=0))
        self.session.add(
            Group(name="group1", owner_email='owner@example.com', description="description", invite_code="test"))
        self.session.commit()
        group1 = self.session.query(Group).filter(and_(
            Group.owner_email == 'owner@example.com', Group.name == 'group1')).one_or_none()

        self.session.add(GroupNotification(
            owner_email='owner@example.com',
            member_email='owner@example.com',
            message="testing",
            resource="graph",
            resource_id=1,
            group_id=group1.id,
            is_read=False,
            type='share'))

        self.session.commit()

        self.session.delete(group1)
        self.session.commit()
        self.assertIsNone(self.session.query(Group).filter(
            Group.name == 'group1').one_or_none())

        self.assertIsNone(self.session.query(GroupNotification).filter(and_(
            GroupNotification.group_id == group1.id, GroupNotification.message == 'testing')).one_or_none())
        self.session.commit()
