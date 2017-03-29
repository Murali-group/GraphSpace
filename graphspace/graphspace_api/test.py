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
	graph1.add_node('a', popup='sample node popup text', label='A')
	graph1.add_node_style('a', shape='ellipse', color='red', width=90, height=90)
	graph1.add_node('b', popup='sample node popup text', label='B')
	graph1.add_node_style('b', shape='ellipse', color='blue', width=40, height=40)

	graph1.add_edge('a', 'b', directed=True, popup='sample edge popup')
	graph1.add_edge_style('a', 'b', directed=True, edge_style='dotted')
	graph1.set_data(data={
		'description': 'my sample graph'
	})
	graph1.set_tags(['sample'])
	return graphspace.post_graph(graph1)['id']


def test_get_graph(graph_id):
	graphspace = GraphSpace('user1@example.com', 'user1')
	return graphspace.get_graph(graph_id)


test_graph_crud()
# print(test_post_graph(name="MyTestGraph14"))
# test_get_graph(77)