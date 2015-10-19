from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'graphspace.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('graphs.urls'), name='base'),
    #url(r'^graphs/$', include('graphs.urls')),
)

handler404 = 'graphs.views.handler_404'
handler500 = 'graphs.views.handler_500'