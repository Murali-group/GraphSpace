'''
This code produces almost the same schema as the original schema used in
the current live version of GraphSpace (as of June 28, 2014). 
There are two differences:
    1. The schema produced by this code does not specify data lengths.
        ex. VARCHAR instead of VARCHAR(x)
    2. Tables in the original schema contain a column named 'id'. 'id' is
       a built-in function in Python so it is not a good practice to use
       it as a variable. Thus 'id' columns are renamed as 'tablename_id'.
       ex. 'id' for user table would be 'user_id'
'''

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Index, ForeignKeyConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import TIMESTAMP
from django.db import models
from django.conf import settings
from sqlalchemy import create_engine

import bcrypt

# Construct a base class for declarative class definitions.
# The new base class will be given a metaclass that produces appropriate Table objects
# and makes the appropriate mapper() calls based on the information provided
# declarativly in the class and any subclasses of the class.
# (Taken from SQLAlchemy API reference)
Base = declarative_base()

#======================== Junction Tables ==========================
# Junction tables for specifying many to many relationships.

# This table stores group-user pairs. A group may contain many users and a user 
# may belong to many groups. The name of the table is 'group_to_user'. 
# It has two columns, 'user_id' and 'group_id', which together constitute the 
# primary key. 'user_id' is a foreign key referring to the 'user_id' column in 
# the 'user' table. 'group_id' is a foreign key referring to the 'group_id' column 
# in the 'group' table.
        
# For each graph, this table stores the groups that the graph belongs to. 
# Note that a graph may belong to multiple groups. 

# For each graph, this table stores tags that the graph has. A graph can have i
# many tags, and a tag can belong to many graphs.


#=================== End of Junction Tables ===================

# ================== Table Definitions ===================
class GroupToUser(Base):
    '''The class representing the schema of the group_to_user table.'''
    __tablename__ = 'group_to_user'

    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    group_id = Column(String, ForeignKey('group.group_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    group_owner = Column(String, ForeignKey('group.owner_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
       
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"))
    user_id = Column(String, ForeignKey('graph.user_id', ondelete="CASCADE", onupdate="CASCADE"))
    layout_id = Column(String, ForeignKey('layout.layout_id', ondelete="CASCADE", onupdate="CASCADE"))
    text = Column(String, nullable = False)
    created = Column(TIMESTAMP, nullable = False)

class GroupToGraph(Base):
    '''The class representing the schema of the group_to_graph table.'''
    __tablename__ = 'group_to_graph'

    group_id = Column(String, ForeignKey('group.group_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    group_owner = Column(String, ForeignKey('group.owner_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    user_id = Column(String, ForeignKey('graph.user_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    modified = Column(TIMESTAMP, nullable = False)

class GraphToTag(Base):
    '''The class representing the schema of the graph_to_tag table.'''
    __tablename__ = 'graph_to_tag'

    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    user_id = Column(String, ForeignKey('graph.user_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    tag_id = Column(String, ForeignKey('graph_tag.tag_id'), primary_key=True)

class TaskCode(Base):
    '''The class representing the schema of the task_code table.'''
    __tablename__ = 'task_code'
    hit_id = Column(String, ForeignKey('task.hit_id', ondelete="CASCADE", onupdate="CASCADE"))
    code = Column(String, primary_key = True)
    created = Column(TIMESTAMP, nullable = False)

class User(Base):
    '''The class representing the schema of the user table.'''
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

class Graph(Base):
    __tablename__ = 'graph'

    # The graph_id and user_id together specify the primary key.     
    graph_id = Column(String, primary_key = True) #id
    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), primary_key = True)
    json = Column(String, nullable = False)
    created = Column(TIMESTAMP, nullable = False)
    modified = Column(TIMESTAMP, nullable = False)
    public = Column(Integer, nullable = True)
    shared_with_groups = Column(Integer, nullable = True)
    default_layout_id = Column(String, nullable = True)

    # specify one to many relationships
    # layouts = relationship("Layout")
    # # Each node can belong to at most one graph. See the 'Node' class for details.
    # nodes = relationship("Node")

    # groups = relationship("Group", backref='graph')
    
    #specify many to many relationship with GraphTag
    # tags = relationship("GraphTag", secondary=graph_to_tag, backref='graph')

class Task(Base):
    '''
        Table that represents the task table.
    '''
    __tablename__ = 'task'

    task_id = Column(Integer, autoincrement=True, primary_key=True)
    task_owner = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    layout_id = Column(String, ForeignKey('layout.layout_id', ondelete="CASCADE", onupdate="CASCADE"))
    created = Column(TIMESTAMP, nullable = False)
    hit_id=Column(String, nullable=False)
    worker_id=Column(String, nullable=False)
    submitted=Column(Integer, nullable=True)
    task_type=Column(String, nullable=False)

class GraphTag(Base):
    '''
        Table of tags that are assigned to each graph to categorize them.
    '''
    __tablename__ = 'graph_tag'
    tag_id = Column(String, primary_key = True) #id

class Feature(Base):
    '''
        Table that holds all the features.
    '''
    __tablename__ = 'feature'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"))
    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = True)
    layout_id = Column(String, ForeignKey('layout.layout_id', ondelete="CASCADE", onupdate="CASCADE"))
    created = Column(TIMESTAMP, nullable = False)
    distance_vector = Column(String, nullable = True)
    pairwise_vector = Column(String, nullable = True)
    num_changes = Column(Integer, nullable = False)
    time_spent = Column(Integer, nullable = False)
    events = Column(String, nullable = False)

class Layout(Base):
    '''
        Table of Layouts to specify how the graphs are viewed on GraphSpace.
        User created layouts will be stored in this table.
    '''
    __tablename__ = 'layout'

    layout_id = Column(Integer, autoincrement=True, primary_key=True)
    # A descriptive name for the layout, provided by the owner_id when creating the i
    # layout in GraphSpace.
    layout_name = Column(String, nullable = False)

    # The id of the user who created the layout. The foreign key constraint ensures 
    # this person is present in the 'user' table. Not that owner_id need not be the 
    # same as user_id since (graph_id, user_id) uniquely identify the graph. 
    # In other words, the owner_id can be the person other than the one who created 
    # the graph (user_id). An implicit rule is that owner_id must belong to some 
    # group that this graph belongs to. However, the database does not enforce this 
    # constraint explicitly. 
    # TODO: Add a database constraint that checks this rule.
    owner_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    # id of the graph that the layout is for
    graph_id = Column(String, nullable = False)
    # id of the user who owns the graph specified by graph_id
    user_id = Column(String, nullable = False)
    # graph layout data in JSON format
    json = Column(String, nullable = False)
    public = Column(Integer, nullable = True)
    shared_with_groups = Column(Integer, nullable = True)
    # when was the last time layout was modified
    times_modified = Column(Integer, nullable = False)
    # If layout is updated (task), save the original layout
    original_json = Column(String, nullable = True)

    # SQLAlchemy's way of creating a multi-column foreign key constraint.
    __table_args__ = (ForeignKeyConstraint([graph_id, user_id], [Graph.graph_id, Graph.user_id], ondelete="CASCADE", onupdate="CASCADE"), {})

class LayoutStatus(Base):
    '''
       Table of layout acceptances/rejections.
    '''
    __tablename__ = 'layout_status'

    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"))
    user_id = Column(String, ForeignKey('graph.user_id', ondelete="CASCADE", onupdate="CASCADE"))
    layout_id = Column(Integer, nullable = False)
    triangle_rating = Column(Integer, nullable = False)
    rectangle_rating = Column(Integer, nullable = False)
    shape_rating = Column(Integer, nullable = False)
    color_rating = Column(Integer, nullable = False)
    created = Column(TIMESTAMP, nullable = False)
    submitted_by = Column(String, nullable = True)

class Node(Base):
    '''
        Table of nodes used in graphs. Same node can be in many graphs, but they are 
        considered to be distinct.
    '''
    __tablename__ = 'node'

    # The primary key contains three columns: node_id, graph_id, and user_id. The same node may appear in different graphs but we consider them to be distinct.
    node_id = Column(String, primary_key = True)
    label = Column(String, nullable = False)
    user_id = Column(String, primary_key = True)
    graph_id = Column(String, primary_key = True)
    modified = Column(TIMESTAMP, primary_key = True)

    # Foregin key contraint to idientify the graph that this node belong to
    __table_args__ = (ForeignKeyConstraint([user_id, graph_id], [Graph.user_id, Graph.graph_id], ondelete="CASCADE", onupdate="CASCADE"), {})

    # one to many relationship with Edge, since a node can have many edges.
    heads = relationship("Edge", foreign_keys="[Edge.user_id, Edge.graph_id, Edge.head_node_id]")
    tails = relationship("Edge", foreign_keys="[Edge.user_id, Edge.graph_id, Edge.head_node_id]")

class PasswordReset(Base):
    __tablename__ = 'password_reset'

    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable = False)
    code = Column(String, nullable = False)
    created = Column(TIMESTAMP, nullable = False)

    #no relationship specified

class Edge(Base):
    '''
        Table of edges that are used on graphs.
    '''
    __tablename__ = 'edge'

    # 3 column primary keys are used to determine which two nodes that this edge connect.
    # each edge connects a head node to a tail node.
    # head node
    user_id = Column(String, nullable = False)
    graph_id = Column(String, nullable = False)
    head_node_id = Column(String, nullable = False)

    # tail node
    tail_node_id = Column(String, nullable = False)

    # label of this edge
    edge_id = Column(String, nullable = True)
    # inicates whether this edge is directed or not.
    directed = Column(Integer, nullable = True)

    id = Column(Integer, autoincrement=True, primary_key=True)
    
    # Foreign key contraints to determine each node.
    __table_args__ = (
            ForeignKeyConstraint([user_id, graph_id, head_node_id], [Node.user_id, Node.graph_id, Node.node_id], ondelete="CASCADE", onupdate="CASCADE"),
            ForeignKeyConstraint([user_id, graph_id, tail_node_id], [Node.user_id, Node.graph_id, Node.node_id], ondelete="CASCADE", onupdate="CASCADE"), {})
    #no relationship specified

class share_graph_event(Base):
    __tablename__ = 'share_graph_event'
    # unique id for each share graph event
    id = Column(Integer, autoincrement=True, primary_key=True)
    # id of the graph shared
    graph_id = Column(String, ForeignKey('graph.graph_id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # id of the owner of the graph which is shared
    owner_id = Column(String, ForeignKey('group.owner_id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # id of the group the graph is shared in
    group_id = Column(String, ForeignKey('group.group_id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # id of the member of the group.
    # Hence there can be multiple share graph events if a owner shares a grap
    # with a group. A share graph event will be created for all the memebers
    # of the group except the owner of the graph (the one who shared it).
    member_id = Column(String, ForeignKey('user.user_id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # timestamp at which the share graph event occured
    share_time = Column(TIMESTAMP, nullable = False)
    # Boolean value to track if notifications is read or not.
    # if True then the notification is active, i.e not read
    is_active = Column(Boolean)

#Create indices
Index('graph_public_idx', Graph.public)
Index('graph_owner_idx', Graph.user_id)
# Table: group. Columns: owner_id
Index('group_idx_owner_id_group_id', Group.owner_id, Group.group_id)
# Table: graph. Columns: user_id
Index('graph_idx_user_graph_id', Graph.user_id, Graph.graph_id)
# Table: graph. Columns: user_id, modified, public
Index('graph_idx_user_id_modified_id_public', Graph.user_id, Graph.graph_id, Graph.modified, Graph.public)
# Table: graph. Columns: modified, user_id, graph_id, public
# Table: graph_to_tag. Columns: graph_id, user_id
Index('graph_to_tag_idx_graph_id_user_id', GraphToTag.graph_id, GraphToTag.user_id, GraphToTag.tag_id)
# Table: graph_to_tag. Columns: tag_id
Index('graph_to_tag_idx_tag_id', GraphToTag.tag_id)
Index('graph_to_tag_idx_user_id', GraphToTag.user_id, GraphToTag.graph_id)
# Table: group_to_graph. Columns: graph_id, user_id
Index('group_to_graph_idx_graph_id_user_id', GroupToGraph.graph_id, GroupToGraph.user_id, GroupToGraph.group_id, GroupToGraph.group_owner)
# Table: group_to_graph. Columns: group_id
Index('group_to_graph_idx_group_id', GroupToGraph.group_id, GroupToGraph.group_owner)
Index('group_to_graph_graph_idx', GroupToGraph.graph_id)
Index('group_to_graph_group_idx', GroupToGraph.group_id)
Index('group_to_graph_user_idx', GroupToGraph.user_id)
# Table: group_to_graph. Columns: graph_id, user_id, group_id.
# Table: group_to_user. Columns: group_id
Index('group_to_user_idx_group_id', GroupToUser.group_id, GroupToUser.user_id, GroupToUser.group_owner)
# Table: group_to_user. Columns: user_id
Index('group_to_user_idx_user_id', GroupToUser.user_id)
# Table: layout. Columns: graph_id, user_id
#Index('layout_idx_graph_id_user_id', Layout.graph_id, Layout.user_id)
# Table: layout. Columns: owner_id
#Index('layout_idx_owner_id', Layout.owner_id)
# Table: node. Columns: graph_id, user_id
Index('node_idx_graph_id_user_id', Node.graph_id, Node.user_id, Node.node_id, Node.label)
Index('node_index_label_graph_id', Node.label)
Index('node_index_node_id_graph_id', Node.node_id)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine(settings.DATABASE_LOCATION, echo=False)
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
