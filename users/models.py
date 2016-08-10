from __future__ import unicode_literals

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from django.conf import settings

config = settings.DATABASES['default']

# Construct a base class for declarative class definitions.
# The new base class will be given a metaclass that produces appropriate Table objects
# and makes the appropriate mapper() calls based on the information provided
# declarativly in the class and any subclasses of the class.
# (Taken from SQLAlchemy API reference)
Base = declarative_base()


# ================== Table Definitions ===================

class User(Base):
    """
    The class representing the schema of the user table.
    """
    __tablename__ = 'user'

    user_id = Column(String, primary_key = True)
    password = Column(String, nullable = False)
    admin = Column(Integer, nullable = True)

    # one to many relationships. TODO: add cascades
    # at most one user can create a graph layout
    layouts = relationship("Layout")
    # each group has at most one user who created it. See the owner_id column in the 'Group' class.
    owned_groups = relationship("Group")
    # each graph has at most one creator.
    graphs = relationship("Graph")
    # ???
    password_reset = relationship("PasswordReset")


class PasswordReset(Base):
    __tablename__ = 'password_reset'

    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    code = Column(String, nullable = False)
    created = Column(TIMESTAMP, nullable = False)

    #no relationship specified

# TODO: change name to Group here and in the db.
class Group(Base):
    __tablename__ = 'group'

    group_id = Column(String, primary_key = True)
    # TODO: describe the difference bewteen group_id and name.
    name = Column(String, nullable = False)
    # Each group has one owner, who must be in the user table. The foreign key
    # statement corresponds to the owned_groups relationship in the 'User' class.
    owner_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False, primary_key = True)
    description = Column(String, nullable = False)

    # This line creates the many-to-many relationship between the User class and the i
    # Group class through the group_to_user junction table. Specifically,
    # it links the 'User' class to the current class using the group_to_user junction
    # table; this is a many to one relationship from 'User' to 'group_to_user'.
    # The backref argument establishes the many to one relationship from 'Group'
    # to 'group_to_user'. An equivalent way to link the two classes is to instead
    # add the following line to User:
    # groups = relationship('Group', secondary=group_to_user, backref='user')
    # users = relationship('User', backref='group')
    # # specifies many-to-many relationship with Graph table
    # graphs = relationship('Graph', backref='group')

class GroupToUser(Base):
    '''The class representing the schema of the group_to_user table.'''
    __tablename__ = 'group_to_user'

    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    group_id = Column(String, ForeignKey('group.group_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    group_owner = Column(String, ForeignKey('group.owner_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)




