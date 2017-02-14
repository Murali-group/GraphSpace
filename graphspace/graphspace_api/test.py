from graphspace.graphs.classes.gsgraph import GSGraph
from graphspace.graphspace_api.client import GraphSpace


def test_graph_crud():
	graph_id = test_post_graph(name='MyTestGraph')
	assert test_get_graph(graph_id)['id'] == graph_id
	test_update_graph(graph_id)
	print test_delete_graph(graph_id)


def test_update_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'a')
	assert graphspace.make_graph_public(graph_id)['is_public'] == 1

def test_delete_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'a')
	return graphspace.delete_graph(graph_id)


def test_post_graph(name=None):
	graphspace = GraphSpace('user1@example.com', 'a')
	graph1 = GSGraph()
	if name is not None:
		graph1.set_name(name)
	graph1.add_node('a')
	graph1.add_node('b')
	graph1.add_edge('a', 'b')
	return graphspace.post_graph(graph1)['id']


def test_get_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'a')
	return graphspace.get_graph(graph_id)


test_graph_crud()
# test_post_graph()
# test_get_graph(77)