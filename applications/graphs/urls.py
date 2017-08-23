from django.conf.urls import url
from applications.graphs import views
from django.views.decorators.csrf import csrf_protect

urlpatterns = [

	url(r'^graphs/$', views.graphs_page, name='graphs'),
	url(r'^graphs/(?P<graph_id>[^/]+)$', views.graph_page, name='graph'),
	url(r'^graphs/(?P<email>[^/]+)/(?P<graph_name>[^/]+)$', views.graph_page_by_name, name='graph_by_name'),
	url(r'^upload$', views.upload_graph_page, name='upload_graph'),

	# AJAX APIs Endpoints

	# Graphs
	url(r'^ajax/graphs/$', views.graphs_ajax_api, name='graphs_ajax_api'),
	url(r'^ajax/graphs/advanced_search$', views.graphs_advanced_search_ajax_api, name='graphs_advanced_search_ajax_api'),
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)$', views.graphs_ajax_api, name='graph_ajax_api'),
	# Graphs Groups
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/groups$', views.graph_groups_ajax_api, name='graph_groups_ajax_api'),
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/groups/(?P<group_id>[^/]+)$', views.graph_groups_ajax_api, name='graph_group_ajax_api'),
	# Graph Nodes
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/nodes/$', views.graph_nodes_ajax_api, name='graph_nodes_ajax_api'),
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/nodes/(?P<node_id>[^/]+)$', views.graph_nodes_ajax_api, name='graph_nodes_ajax_api'),
	# Graph Edges
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/edges/$', views.graph_edges_ajax_api, name='graph_edges_ajax_api'),
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/edges/(?P<edge_id>[^/]+)$', views.graph_edges_ajax_api, name='graph_edges_ajax_api'),
	# Graph Layouts
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/layouts/$', views.graph_layouts_ajax_api, name='graph_layouts_ajax_api'),
	url(r'^ajax/graphs/(?P<graph_id>[^/]+)/layouts/(?P<layout_id>[^/]+)$', views.graph_layouts_ajax_api, name='graph_layouts_ajax_api'),

	# REST APIs Endpoints

	# Graphs
	url(r'^api/v1/graphs/$', views.graphs_rest_api, name='graphs_rest_api'),
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)$', views.graphs_rest_api, name='graph_rest_api'),
	# Graphs Groups
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/groups$', views.graph_groups_rest_api, name='graph_groups_rest_api'),
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/groups/(?P<group_id>[^/]+)$', views.graph_groups_rest_api, name='graph_group_rest_api'),
	# Graph Nodes
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/nodes/$', views.graph_nodes_rest_api, name='graph_nodes_rest_api'),
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/nodes/(?P<node_id>[^/]+)$', views.graph_nodes_rest_api, name='graph_nodes_rest_api'),
	# Graph Edges
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/edges/$', views.graph_edges_rest_api, name='graph_edges_rest_api'),
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/edges/(?P<edge_id>[^/]+)$', views.graph_edges_rest_api, name='graph_edges_rest_api'),
	# Graph Layouts
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/layouts/$', views.graph_layouts_rest_api, name='graph_layouts_rest_api'),
	url(r'^api/v1/graphs/(?P<graph_id>[^/]+)/layouts/(?P<layout_id>[^/]+)$', views.graph_layouts_rest_api, name='graph_layouts_rest_api'),

]
