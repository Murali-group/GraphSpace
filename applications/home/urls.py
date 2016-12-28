from applications.home import views
from django.conf.urls import url

urlpatterns = [
	url(r'^$', views.home_page, name='home'),
	url(r'^login/$', views.login, name='login'),
	url(r'^register/$', views.register, name='register'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^index/$', views.home_page, name='home'),
	url(r'^index$', views.home_page, name='home'),
	url(r'^features/$', views.home_page, name='features'),
	url(r'^help_tutorial/$', views.home_page, name='help_tutorial'),
	url(r'^help_about/$', views.home_page, name='help_about'),
]
