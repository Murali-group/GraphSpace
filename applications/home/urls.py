from django.conf.urls import patterns, url
from applications.home import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^index/$', views.index, name='index'),
	url(r'^index/$', views.index, name='index'),
	url(r'^graphs/$', views.index, name='graphs'),
	url(r'^groups/$', views.index, name='groups'),
	url(r'^features/$', views.index, name='features'),
	url(r'^help_tutorial/$', views.index, name='help_tutorial'),
	url(r'^help_about/$', views.index, name='help_about'),
]
