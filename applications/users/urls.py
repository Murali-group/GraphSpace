from applications.users import views
from django.conf.urls import url

urlpatterns = [

	url(r'^groups/$', views.groups_page, name='groups'),
	url(r'^groups/(?P<group_id>[^/]+)$', views.group_page, name='group'),

	url(r'^javascript/groups/$', views.groups, name='groups_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)$', views.groups, name='groups_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)/members$', views.group_members, name='group_members_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)/members/(?P<member_id>[^/]+)$', views.group_members, name='group_members_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)/graphs$', views.group_graphs, name='group_graphs_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)/graphs/(?P<graph_id>[^/]+)$', views.group_graphs, name='group_graphs_api'),
]