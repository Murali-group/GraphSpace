import models
import graphs.util.db_init as db_init

data_connection = db_init.db


def add_graph(graph_id, user_id, json, public=0, shared_with_groups=0, default_layout_id=None):
	"""
	Inserts a graph with given graph_id for a user with given user_id.

	:param graph_id: ID of the graph
	:param user_id: ID of the user creating the graph
	:param json: JSON of graph
	:param public: 1 if graph is public else 0
	:param shared_with_groups: 1 if graph is shared with any group else 0
	:param default_layout_id: layout id of default layout for the graph.
	:return: None
	"""


def get_graph(graph_id, user_id):
	"""
	Get a graph with given graph_id and user_id.

	:param graph_id: ID of the graph
	:param user_id: ID of the user who created the graph
	:return: Graph
	"""


def update_graph(graph_id, user_id, updated_graph):
	"""
	Update the graph with given updated graph entry.

	:param graph_id: ID of the graph
	:param user_id: ID of the user who created the graph
	:param updated_graph: updated graph row entry
	:return: None
	"""


def delete_graph(graph_id, user_id):
	"""
	Delete a graph with given graph_id and user_id.

	:param graph_id: ID of the graph
	:param user_id: ID of the user who created the graph
	:return: None
	"""


def add_graph_tag(tag_id):
	"""
	Add a graph tag.

	:param tag_id: Graph Tag
	:return: None
	"""


def delete_graph_tag(tag_id):
	"""
	Delete a graph tag.

	:param tag_id: Graph Tag
	:return: None
	"""


def update_graph_tag(tag_id, updated_tag_id):
	"""
	Update the graph tag with give tag_id to updated_tag_id.

	:param tag_id: Original Graph Tag
	:param updated_tag_id: Updated Graph Tag
	:return: None
	"""


def get_all_graph_tag():
	"""
	Get all graph tags.

	:return: List of GraphTags
	"""


def add_graph_to_tag(graph_id, user_id, tag_id):
	"""
	Add a graph to tag relationship.

	:param graph_id: ID of the graph.
	:param user_id: ID of the user who created the graph.
	:param tag_id: Graph Tag.
	:return: None
	"""


def delete_graph_to_tag(graph_id, user_id, tag_id):
	"""
	Delete a graph to tag relationship.

	:param graph_id: ID of the graph.
	:param user_id: ID of the user who created the graph.
	:param tag_id: Graph Tag.
	:return: None
	"""


def get_all_graphs_by_tag_id(tag_id):
	"""
	Get all graphs with given tag_id

	:param tag_id: Graph Tag
	:return: List of Graphs.
	"""


def get_graphs_by_user_id(user_id):
	"""
	Get all graphs created by a user with given user_id

	:param user_id: ID of the user
	:return: List of Graphs.
	"""


def add_group_to_graph(group_id, group_owner, graph_id, user_id):
	"""
	Add a group to graph relationship.

	:param group_id: ID of the group.
	:param group_owner: Unique ID of the user who owns the group.
	:param graph_id: ID of the graph.
	:param user_id: ID of the user.
	:return: None
	"""

def delete_group_to_graph(group_id, group_owner, graph_id, user_id):
	"""
	Add a group to graph relationship.

	:param group_id: ID of the group.
	:param group_owner: Unique ID of the user who owns the group.
	:param graph_id: ID of the graph.
	:param user_id: ID of the user.
	:return: None
	"""


def get_graphs_by_group(group_id, group_owner):
	"""
	Get all graphs belonging to group with given group_id and given group_owner.
	:param group_id: ID of the group.
	:param group_owner: user ID of the owner of the group.
	:return: List of Graphs.
	"""


def add_node(node_id, user_id, graph_id):
	"""

	:param node_id: ID of the node
	:param user_id: ID of the user
	:param graph_id: ID of the graph
	:return: None
	"""

