from django.conf.urls import url
from applications.notifications import views
from django.views.decorators.csrf import csrf_protect


urlpatterns = [
	
	# Show notification page
	url(r'^notifications/$', views.notifications_page, name='notification')
]