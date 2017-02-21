from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),

	url(r'^', include('applications.home.urls')),
	url(r'^', include('applications.graphs.urls')),
	url(r'^', include('applications.users.urls')),
	url(r'^', include('applications.uniprot.urls')),
]

handler404 = 'graphs.views.handler_404'
handler500 = 'graphs.views.handler_500'
