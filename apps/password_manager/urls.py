from django.conf.urls import url, include

from .views import (
	password_manager, create_password, edit_password, delete_password, check_password,
	generate_link, access_link)


urlpatterns = [
	url(r'^$', password_manager, name='password_manager'),
	url(r'^create_password$', create_password, name='create_password'),
	url(r'^edit_password/(?P<password_pk>\d+)$', edit_password, name='edit_password'),
	url(r'^delete_password$', delete_password, name='delete_password'),
	url(r'^check_password$', check_password, name='check_password'),

	url(r'^generate_link/(?P<obj_pk>\d+)$', generate_link, name='generate_link'),
	url(r'^access_link/(?P<link>.+)$', access_link, name='access_link'),

	url(r'^api/', include('apps.password_manager.api.urls', namespace='api')),
]
