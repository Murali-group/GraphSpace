from django.conf.urls import url
from applications.graphs import views

urlpatterns = [

	url(r'^graphs/$', views.graphs_page, name='graphs'),
	url(r'^graphs/(?P<graph_id>[^/]+)$', views.graph_page, name='graph'),
	url(r'^upload$', views.upload_graph_page, name='upload_graph'),

	# APIs ENDPOINTS
	url(r'^javascript/graphs/$', views.gs_graphs, name='graphs_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)$', views.gs_graphs, name='graphs_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)$', views.gs_graphs, name='graphs_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)/groups$', views.graph_groups, name='graph_groups_api'),
	url(r'^javascript/graphs/(?P<graph_id>[^/]+)/groups/(?P<group_id>[^/]+)$', views.graph_groups, name='group_graphs_api'),




	# url(r'^graphs/(?P<graph_owner>\b[A-Z0-9a-z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,4}\b)/(?P<graphname>.+)/$', views.view_graph, name='view_graph')
]
