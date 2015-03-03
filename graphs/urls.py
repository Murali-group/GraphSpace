from django.conf.urls import patterns, url

from graphs import views

urlpatterns = patterns('', 
        # name parameter indicates the name of the view. This name
        # can be accessed from respective html files using Django 
        # template language.

        # main page
        url(r'^download/$', views.download, name='download'),
        url(r'^index/$', views.index, name='index'),
        url(r'^$', views.index, name='index'),
        url(r'^index/logout/$', views.logout, name='logout'),

        # id of nodes/edges
        url(r'^retrieveIDs/$', views.retrieveIDs, name='retrieveIDs'),
        
        # graphs page
        url(r'^graphs/$', views.graphs, name='graphs'),
        url(r'^graphs/shared/$', views.shared_graphs, name='shared_graphs'),
        url(r'^graphs/public/$', views.public_graphs, name='public_graphs'),
        url(r'^graphs/all/$', views.all_graphs, name='all_graphs'),
        
        # view graph page. This contains regular expression to catch url in the form of the following:
        # /graphs/email_address/graph_id/
        # regex from http://www.regular-expressions.info/email.html
        # <uid> and <gid> are variable names that are passed as parameters
        # into the views.view_graph function.
        url(r'^graphs/(?P<uid>\b[A-Z0-9a-z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,4}\b)/(?P<gid>.+)/layout/$', views.save_layout, name='save_layout'),
        url(r'^graphs/(?P<uid>\b[A-Z0-9a-z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,4}\b)/(?P<gid>.+)/$', views.view_graph, name='view_graph'),

        url(r'^json/(?P<uid>\b[A-Z0-9a-z._%+-]+@[A-Z0-9a-z.-]+\.[A-Za-z]{2,4}\b)/(?P<gid>.+)/$', views.view_json, name='view_json'),

        # groups page
        url(r'^groups/$', views.groups, name='groups'),
        url(r'^groups/member/$', views.groups_member, name='groups_member'),
        # url(r'^groups/public/$', views.public_groups, name='public_groups'),
        url(r'^groups/all/$', views.all_groups, name='all_groups'),
        url(r'^groups/(?P<group_id>.+)/$', views.graphs_in_group, name="graphs_in_group"),
        url(r'^add/(?P<groupname>.+)/$', views.create_group, name='create_group'),

        # help page
        url(r'^help/$', views.help, name='help'),
        url(r'^help/tutorials/$', views.help_tutorials, name='help_tutorials'),
        url(r'^help/graphs/$', views.help_graphs, name='help_graphs'),
        url(r'^help/restapi/$', views.help_restapi, name='help_restapi'),
        url(r'^help/jsonref/$', views.help_jsonref, name='help_jsonref'),
        url(r'^help/about/$', views.help_about, name='help_about'),

        # register page
        url(r'^register/$', views.register, name='register'),

        # Change name of layout
        url(r'^changeLayoutName/$', views.changeLayoutName, name='changeLayoutName'),

        # Delete layout
        url(r'^deleteLayout/$', views.deleteLayout, name='deleteLayout'),

        # Get all groups for a graph
        url(r'^getGroupsForGraph/$', views.getGroupsForGraph, name='getGroupsForGraph'),

        # Shares graphs with specified groups
        url(r'^shareGraphWithGroups/$', views.shareGraphWithGroups, name='shareGraphWithGroups'),

        # Make Layout public
        url(r'^makeLayoutPublic/$', views.makeLayoutPublic, name='makeLayoutPublic'),
        # forgot endpoint
        url(r'^forgot/$', views.sendResetEmail, name='forgot'),

        # reset endpoint
        url(r'^reset/$', views.resetLink, name='reset'),
        url(r'^resetPassword/$', views.resetPassword, name='resetPassword'),

        # tags
        url(r'^api/tags/user/(?P<username>.+)/(?P<graphname>.+)/$', views.get_all_tags_for_graph, name='get_all_tags_for_graph'),
        url(r'^api/tags/user/(?P<username>.+)/$', views.get_tags_for_user, name='get_tags_for_user'),

        #REST API for graphs
        url(r'^api/users/graphs/(?P<graphname>.+)/share/(?P<groupname>.+)/$', views.share_graph, name='share_graph'),
        url(r'^api/users/graphs/(?P<graphname>.+)/unshare/(?P<groupname>.+)/$', views.unshare_graph, name='unshare_graph'),
        url(r'^api/users/(?P<user_id>.+)/graph/add/(?P<graphname>.+)/$', views.upload_graph, name='upload_graph'),
        url(r'^api/users/(?P<user_id>.+)/graph/get/(?P<graphname>.+)/$', views.retrieve_graph, name='retrieve_graph'),
        url(r'^api/users/(?P<user_id>.+)/graph/delete/(?P<graphname>.+)/$', views.remove_graph, name='remove_graph'),
        url(r'^api/users/(?P<user_id>.+)/graphs/$', views.view_all_graphs_for_user, name='view_all_graphs_for_user'),

        #REST API for groups
        url(r'^api/groups/get/$', views.get_groups, name='get_groups'),
        url(r'^api/groups/delete/(?P<groupname>.+)/$', views.delete_group, name='delete_group'),
        url(r'^api/groups/add/(?P<groupname>.+)/$', views.add_group, name='add_group'),
        url(r'^api/groups/(?P<groupname>.+)/adduser/(?P<user_id>.+)/$', views.add_user_to_group, name='add_user_to_group'),
        url(r'^api/groups/(?P<groupname>.+)/removeuser/(?P<user_id>.+)/$', views.remove_user_from_group, name='remove_user_from_group'),
        url(r'^api/groups/(?P<groupname>.+)/get/$', views.get_group, name='get_group'), # needs more work
        url(r'^api/users/(?P<user_id>.+)/groups/$', views.get_group_for_user, name='get_group_for_user'),
        )

