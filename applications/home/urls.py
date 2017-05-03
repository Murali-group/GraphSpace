from applications.home import views
from django.conf.urls import url

urlpatterns = [
	url(r'^$', views.home_page, name='home'),
	url(r'^images/(.*)$', views.images, name='images'),
	url(r'^login/$', views.login, name='login'),
	url(r'^register/$', views.register, name='register'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^index/$', views.home_page, name='home'),
	url(r'^index$', views.home_page, name='home'),
	url(r'^features/$', views.features_page, name='features'),
	url(r'^help/$', views.help_page, name='help'),
	url(r'^about_us/$', views.about_us_page, name='about_us'),
	url(r'^forgot_password/$', views.forgot_password_page, name='forgot_password'),
	url(r'^reset_password/$', views.reset_password_page, name='reset_password'),
]
