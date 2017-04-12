from applications.uniprot import views
from django.conf.urls import url

urlpatterns = [

	# AJAX APIs Endpoints

	# Groups
	url(r'^ajax/aliases/$', views.uniprot_alias_ajax_api, name='uniprot_alias_ajax_api'),
]