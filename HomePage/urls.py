"""HomePage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from apps.search_app.views import search_app
from apps.change_styling.views import change_styling

urlpatterns = [
	url(r'^', include('apps.search_app.urls', namespace='search_app', app_name='search_app')),
    url(r'^change_styling/', include('apps.change_styling.urls', namespace='change_styling', app_name='change_styling')),
    url(r'^tree_traversal/', include('apps.tree_traversal.urls', namespace='tree_traversal', app_name='tree_traversal')),
    url(r'^codility/', include('apps.codility.urls', namespace='codility', app_name='codility')),
    url(r'^mpl_graph/', include('apps.mpl_graph.urls', namespace='mpl_graph', app_name='mpl_graph')),
    url(r'^julia_set/', include('apps.julia_set.urls', namespace='julia_set', app_name='julia_set')),
    url(r'^wallpaper/', include('apps.wallpaper.urls', namespace='wallpaper', app_name='wallpaper')),
    url(r'^scikit_chart/', include('apps.scikit_chart.urls', namespace='scikit_chart', app_name='scikit_chart')),
    url(r'^auth_chat/', include('apps.auth_chat.urls', namespace='auth_chat', app_name='auth_chat')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
