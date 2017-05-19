from django.contrib import admin

from .models import Catalog, Item

admin.site.register(Catalog)
admin.site.register(Item)
