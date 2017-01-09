from applications.users import views
from django.conf.urls import url

urlpatterns = [

	url(r'^groups/$', views.groups_page, name='groups'),
	url(r'^groups/(?P<group_id>[^/]+)$', views.group_page, name='group'),

	# AJAX APIs Endpoints

	# Groups
	url(r'^javascript/groups/$', views.groups_ajax_api, name='groups_ajax_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)$', views.groups_ajax_api, name='groups_ajax_api'),
	# Group Members
	url(r'^javascript/groups/(?P<group_id>[^/]+)/members$', views.group_members_ajax_api, name='group_members_ajax_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)/members/(?P<member_id>[^/]+)$', views.group_members_ajax_api, name='group_members_ajax_api'),
	# Group Graphs
	url(r'^javascript/groups/(?P<group_id>[^/]+)/graphs$', views.group_graphs_ajax_api, name='group_graphs_ajax_api'),
	url(r'^javascript/groups/(?P<group_id>[^/]+)/graphs/(?P<graph_id>[^/]+)$', views.group_graphs_ajax_api, name='group_graphs_ajax_api'),

	# REST APIs Endpoints

	# Groups
	url(r'^api/v1/groups/$', views.groups_rest_api, name='groups_rest_api'),
	url(r'^api/v1/groups/(?P<group_id>[^/]+)$', views.groups_rest_api, name='groups_rest_api'),
	# Group Members
	url(r'^api/v1/groups/(?P<group_id>[^/]+)/members$', views.group_members_rest_api, name='group_members_rest_api'),
	url(r'^api/v1/groups/(?P<group_id>[^/]+)/members/(?P<member_id>[^/]+)$', views.group_members_rest_api, name='group_members_rest_api'),
	# Group Graphs
	url(r'^api/v1/groups/(?P<group_id>[^/]+)/graphs$', views.group_graphs_rest_api, name='group_graphs_rest_api'),
	url(r'^api/v1/groups/(?P<group_id>[^/]+)/graphs/(?P<graph_id>[^/]+)$', views.group_graphs_rest_api, name='group_graphs_rest_api'),
]