from django.conf.urls import url
from applications.graphs import views

urlpatterns = [

	url(r'^graphs/$', views.graphs_page, name='graphs'),
	url(r'^graphs/(?P<graph_id>[^/]+)$', views.graph_page, name='graph'),
	url(r'^upload$', views.upload_graph_page, name='upload_graph'),


	# APIs ENDPOINTS
	url(r'^javascript/graphs/$', views.gs_graphs, name='graphs_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)$', views.gs_graphs, name='graph_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)/groups$', views.graph_groups, name='graph_groups_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)/groups/(?P<group_id>[^/]+)$', views.graph_groups, name='graph_group_api'),

	url(r'^javascript/nodes/$', views.nodes, name='nodes_api'),
	url(r'^javascript/nodes/(?P<node_id>[^/]+)$', views.nodes, name='node_api'),

	url(r'^javascript/edges/$', views.edges, name='edges_api'),
	url(r'^javascript/edges/(?P<edge_id>[^/]+)$', views.edges, name='edge_api'),

	url(r'^javascript/layouts/$', views.layouts, name='layouts_api'),
	url(r'^javascript/layouts/(?P<layout_id>[^/]+)$', views.layouts, name='layout_api'),
]
