from django.conf.urls import url, include

from .views import password_manager, create_password, edit_password, delete_password, check_password


urlpatterns = [
	url(r'^$', password_manager, name='password_manager'),
	url(r'^create_password$', create_password, name='create_password'),
	url(r'^edit_password/(?P<password_pk>\d+)$', edit_password, name='edit_password'),
	url(r'^delete_password$', delete_password, name='delete_password'),
	url(r'^check_password$', check_password, name='check_password'),

	# url(r'^api/', include('apps.password_manager.api.urls', namespace='password_manager_api', app_name='password_manager_api')),
	url(r'^api/', include('apps.password_manager.api.urls', namespace='api')),
]
