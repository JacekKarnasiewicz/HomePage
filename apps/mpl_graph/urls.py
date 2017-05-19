from django.conf.urls import url

from .views import mpl_graph


urlpatterns = [
	url(r'^$', mpl_graph, name='mpl_graph'),
]
