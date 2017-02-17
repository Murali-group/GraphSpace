from graphspace.graphs.classes.gsgraph import GSGraph
from graphspace.graphspace_api.client import GraphSpace


def test_graph_crud():
	graph_id = test_post_graph(name='MyTestGraph')
	assert test_get_graph(graph_id)['id'] == graph_id
	test_update_graph(graph_id)
	print test_delete_graph(graph_id)


def test_update_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'user1')
	assert graphspace.make_graph_public(graph_id)['is_public'] == 1


def test_delete_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'user1')
	return graphspace.delete_graph(graph_id)


def test_post_graph(name=None):
	graphspace = GraphSpace('user1@example.com', 'user1')
	graph1 = GSGraph()
	if name is not None:
		graph1.set_name(name)
	graph1.add_node('a', graph1.construct_node_properties_dict('a', shape='triangle', label='A', color='#ACFA58', width=90, height=40))
	graph1.add_node('b', graph1.construct_node_properties_dict('b', shape='ellipse', label='B', color='red', width=90, height=40))
	graph1.add_edge('a', 'b', graph1.construct_edge_properties_dict('a', 'b', edge_style='dotted'))
	return graphspace.post_graph(graph1)['id']


def test_get_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'user1')
	return graphspace.get_graph(graph_id)


# test_graph_crud()
test_post_graph(name="MyTestGraph1")
# test_get_graph(77)