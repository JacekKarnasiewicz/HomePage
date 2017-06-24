from django.conf.urls import url

from .views import password_manager


urlpatterns = [
	url(r'^$', password_manager, name='password_manager'),
]
