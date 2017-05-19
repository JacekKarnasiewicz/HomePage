from django.conf.urls import url

from .views import tree_traversal


urlpatterns = [
	url(r'^$', tree_traversal, name='tree_traversal'),
]
