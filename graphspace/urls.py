
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views
from applications.home.forms import LoginForm
admin.autodiscover()


urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('applications.home.urls')),
	url(r'^login/$', views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}),
	url(r'^logout/$', views.logout, {'next_page': '/login'}),
]

handler404 = 'graphs.views.handler_404'
handler500 = 'graphs.views.handler_500'