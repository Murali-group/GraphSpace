from django.conf.urls import url
from applications.graphs import views

urlpatterns = [
	url(r'^graphs/$', views.search, name='graphs'),
	url(r'^graphs/shared/$', views.shared_graphs, name='shared_graphs'),
	url(r'^graphs/public/$', views.public_graphs, name='public_graphs'),
	url(r'^graphs/upload/$', views.upload_graph_through_ui, name='upload_graph_through_ui'),
	url(r'^graphs/(?P<graph_owner>\b[A-Z0-9a-z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,4}\b)/(?P<graphname>.+)/$', views.view_graph, name='view_graph')
]
