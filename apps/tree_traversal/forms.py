from django import forms
from django.utils.html import mark_safe

from mptt.forms import TreeNodeChoiceField

from .models import Catalog, Item

class CatalogFormAdd(forms.ModelForm):
	parent = TreeNodeChoiceField(
		label='Parent',
		queryset=Catalog.objects.all(),
		required=False,
		level_indicator=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'),
	)

	class Meta:
		model = Catalog
		fields = ('name', 'parent')


class CatalogFormRemove(forms.Form):
	parent = TreeNodeChoiceField(
		label='Parent',
		queryset=Catalog.objects.all(),
		required=False,
		level_indicator=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'),
	)

	def save(self):
		self.cleaned_data['parent'].delete()


class ItemFormAdd(forms.ModelForm):
	catalog = TreeNodeChoiceField(
		label='Catalog',
		queryset=Catalog.objects.all(),
		required=False,
		level_indicator=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'),
	)

	class Meta:
		model = Item
		fields = ('name', 'link', 'description', 'catalog')


class ItemFormRemove(forms.Form):
	item = forms.ModelChoiceField(
		label='Item',
		queryset=Item.objects.all(),
		required=False
	)

	def save(self):
		self.cleaned_data['item'].delete()
