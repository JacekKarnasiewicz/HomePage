from django.contrib import admin

from .models import Applications

class ApplicationsModelAdmin(admin.ModelAdmin):
	list_display = ['name', 'tags', 'url_name', 'visible']
	list_editable = ['url_name']

admin.site.register(Applications, ApplicationsModelAdmin)
