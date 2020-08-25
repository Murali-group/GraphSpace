from sqlalchemy import and_, or_, desc, asc, event
from sqlalchemy.orm import joinedload, subqueryload
from graphspace.wrappers import with_session
from applications.comments.models import *
from applications.graphs.dal import *
from applications.discussions.dal import *
from applications.users.dal import *
from applications.users.models import *
import graphspace.signals as socket
from graphspace.database import *


@with_session
def add_comment(db_session, text, owner_email=None, is_closed=0, parent_comment_id=None):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    text: string
        Comment message.
    owner_email: string
        Email ID of user who comment on the graph.
    is_closed: Integer
        Integer indicating if the comment is closed or not.
    parent_comment_id:Integer
        Unique ID of parent comment.

    Returns
    -------
    comment: Object
        Comment Object.

    """
    comment = Comment(text=text, owner_email=owner_email, is_closed=is_closed, parent_comment_id=parent_comment_id)
    db_session.add(comment)
    return comment


@with_session
def add_comment_to_graph(db_session, comment_id, graph_id, layout_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    comment_id: Integer
        Unique ID of comment.
    graph_id: Integer
        Unique ID of graph.
    layout_id: Integer
        Unique ID of layout.

    Returns
    -------
    comment_to_graph: Object.
        CommentToGraph Object.

    """
    comment_to_graph = CommentToGraph(comment_id=comment_id, graph_id=graph_id, layout_id=layout_id)
    db_session.add(comment_to_graph)
    return comment_to_graph


@with_session
def add_comment_to_edge(db_session, comment_id, edge_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    comment_id: Integer
        Unique ID of comment.
    edge_id: Integer
        Unique ID of edge.

    Returns
    -------
    comment_to_edge: Object.
        CommentToEdge Object.

    """
    comment_to_edge = CommentToEdge(comment_id=comment_id, edge_id=edge_id)
    db_session.add(comment_to_edge)
    return comment_to_edge


@with_session
def add_comment_to_node(db_session, comment_id, node_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    comment_id: Integer
        Unique ID of comment.
    node_id: Integer
        Unique ID of node.

    Returns
    -------
    comment_to_node: Object
        CommentToNode Object

    """
    comment_to_node = CommentToNode(comment_id=comment_id, node_id=node_id)
    db_session.add(comment_to_node)
    return comment_to_node


@with_session
def get_comment_by_graph_id(db_session, graph_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    graph_id: Integer
        Unique ID of graph.

    Returns
    -------
    return value: tuple
    Count, List of comments associated with the graph.

    """
    query = db_session.query(Comment)
    query = query.filter(CommentToGraph.graph_id == graph_id)
    query = query.filter(Comment.id == CommentToGraph.comment_id)
    query2 = db_session.query(Comment).filter(Comment.parent_comment_id == CommentToGraph.graph_id)
    query3 = query.union(query2)

    return query3.count(), query3.all()


@with_session
def get_comment_by_id(db_session, id):
    """

    Parameters
    ----------
    db_session: object
        Database session.
    id: Integer
        Unique ID of comment.

    Returns
    -------
    comment: Object
        Comment Object.

    """
    comment = db_session.query(Comment).filter(Comment.id == id).one_or_none()
    return comment


@with_session
def get_comment_to_graph(db_session, id):
    """

    Parameters
    ----------
    db_session: object
        Database session.
    id: Integer
        Unique ID of comment.

    Returns
    -------
    comment: Object
        Comment Object.

    """
    comment_to_graph = db_session.query(CommentToGraph).filter(CommentToGraph.comment_id == id).one_or_none()
    return comment_to_graph


@with_session
def get_user_emails_by_graph_id(db_session, graph_id):
    """

    Parameters
    ----------
    db_session: object
        Database session.
    graph_id: Integer
        Unique ID of the graph.

    Returns
    -------
    return value: List
        List of all email IDs who have permission to read the graph.

    """
    query = db_session.query(User, GroupToGraph, GroupToUser)
    query = query.filter(GroupToGraph.graph_id == graph_id)
    query = query.filter(GroupToUser.group_id == GroupToGraph.group_id)
    query = query.filter(User.id == GroupToUser.user_id)
    return query.all()


@with_session
def get_nodes_by_comment_id(db_session, comment_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    comment_id: Integer
        Unique ID of the comment.

    Returns
    -------
    return value: List
        List of all nodes associated with the given comment.

    """
    query = db_session.query(Comment, CommentToNode, Node)
    query = query.filter(comment_id == CommentToNode.comment_id)
    query = query.filter(CommentToNode.node_id == Node.id)
    return query.all()


@with_session
def get_edges_by_comment_id(db_session, comment_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    comment_id: Integer
        Unique ID of the comment.

    Returns
    -------
    return value: List
        List of all edges associated with the given comment.

    """
    query = db_session.query(Comment, CommentToEdge, Edge)
    query = query.filter(comment_id == CommentToEdge.comment_id)
    query = query.filter(CommentToEdge.edge_id == Edge.id)
    return query.all()


@with_session
def get_owner_email_by_graph_id(db_session, graph_id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    graph_id: Integer
        Unique ID of graph.

    Returns
    -------
    return value: List
        List of all User Objects.

    """
    query = db_session.query(User, Graph)
    query = query.filter(User.email == Graph.owner_email)
    return query.all()


@with_session
def update_comment(db_session, id, updated_comment):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    id: Integer
        Unique ID of comment.
    updated_comment: dict
        Dict containing key, value pairs of updated_comment.

    Returns
    -------
    comment: Object
        Updated Comment Object.

    """
    comment = db_session.query(Comment).filter(Comment.id == id).one_or_none()
    if updated_comment['is_closed'] == 1:
        query = db_session.query(Comment).filter(Comment.parent_comment_id == id).all()
        for ele in query:
            for (key, value) in updated_comment.items():
                setattr(ele, key, value)
    elif updated_comment['is_closed'] == 0:
        query = db_session.query(Comment).filter(Comment.parent_comment_id == id).all()
        for ele in query:
            for (key, value) in updated_comment.items():
                setattr(ele, key, value)
    for (key, value) in updated_comment.items():
        setattr(comment, key, value)

    comment_to_graph = get_comment_to_graph(Database().session(), comment.id)
    send_comment(comment, comment_to_graph, event="update")
    return comment


@with_session
def delete_comment(db_session, id):
    """

    Parameters
    ----------
    db_session: Object
        Database session.
    id: Integer
        Unique ID of comment.

    Returns
    -------
    comment: Object
        Deleted Comment Object.

    """
    comment = db_session.query(Comment).filter(Comment.id == id).one_or_none()
    for reaction in comment.reactions:
        db_session.delete(reaction)
    comment_to_graph = get_comment_to_graph(db_session, comment.id)
    send_comment(comment, comment_to_graph, event="delete")
    query = db_session.query(Comment).filter(Comment.parent_comment_id == id).all()
    for ele in query:
        for reaction in ele.reactions:
            db_session.delete(reaction)
        db_session.delete(ele)
    db_session.delete(comment)
    return comment


def send_comment(comment, comment_to_graph, event):

    users_list = get_user_emails_by_graph_id(Database().session(), comment_to_graph.graph_id)
    users_list = [ele[0] for ele in users_list]
    owner_list = get_owner_email_by_graph_id(Database().session(), comment_to_graph.graph_id)
    owner_list = [ele[0] for ele in owner_list]
    socket.send_comment(comment=comment, type="private", users=owner_list + users_list, event=event)
