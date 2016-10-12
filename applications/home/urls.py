from applications.home import views
from django.conf.urls import url

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login/$', views.login, name='login'),
	url(r'^register/$', views.register, name='register'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^index/$', views.index, name='index'),
	url(r'^index/$', views.index, name='index'),
	url(r'^features/$', views.index, name='features'),
	url(r'^help_tutorial/$', views.index, name='help_tutorial'),
	url(r'^help_about/$', views.index, name='help_about'),
]
