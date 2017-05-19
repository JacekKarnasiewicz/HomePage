from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.test import TestCase

from .forms import CatalogFormAdd, CatalogFormRemove, ItemFormAdd, ItemFormRemove
from .models import Catalog, Item
from .views import tree_traversal


class ModelTest(TestCase):

	def setUp(self):
		self.catalog = Catalog.objects.create(name='Root')
		self.item = Item.objects.create(name='Item 1', catalog=self.catalog)

	def test_tree_relationships(self):
		cat = Catalog.objects.create(name='Documents', parent=self.catalog)
		self.assertIn(cat, self.catalog.get_children())
		self.assertIn(self.catalog, cat.get_ancestors())

		Item.objects.create(name='File 1', catalog=cat)
		Item.objects.create(name='File 2', catalog=cat)
		Item.objects.create(name='File 3', catalog=cat)
		self.assertEqual(cat.item_set.count(), 3)

	def test_delete_branch(self):
		cat = Catalog.objects.create(name='Documents')
		item_first = Item.objects.create(name='Item 2', catalog=cat)
		item_second = Item.objects.create(name='Item 3', catalog=cat)

		self.assertIn(item_first, Item.objects.all())
		self.assertIn(item_second, Item.objects.all())

		cat.delete()
		self.assertNotIn(item_first, Item.objects.all())
		self.assertNotIn(item_second, Item.objects.all())

	def test_unique_names(self):
		# problem with transactions and intentionally triggering an exception
		with transaction.atomic(), self.assertRaises(IntegrityError):
			Catalog.objects.create(name='Root')

		with transaction.atomic(), self.assertRaises(IntegrityError):
			Item.objects.create(name='Item 1', catalog=self.catalog)

	def test_required_catalog_field(self):
		with transaction.atomic(), self.assertRaises(IntegrityError):
			Item.objects.create(name='Item 2')

	# test model methods
	def test_string_representation(self):
		self.assertEqual(str(self.catalog), self.catalog.name)
		self.assertEqual(str(self.item), self.item.name)


class FormTest(TestCase):

	def setUp(self):
		self.catalog = Catalog.objects.create(name='Root')
		self.item = Item.objects.create(name='Item 1', catalog=self.catalog)

	def test_save_CatalogFormAdd_valid_form(self):
		form = CatalogFormAdd(data={'name': 'Documents', 'parent': self.catalog.pk})
		self.assertTrue(form.is_valid())
		cat = form.save()
		self.assertIn(cat, Catalog.objects.all())

	def test_save_CatalogFormAdd_invalid_form(self):
		form = CatalogFormAdd(data={})
		self.assertFalse(form.is_valid())
		with self.assertRaises(ValueError):
			form.save()

		self.assertEqual(form.errors['name'], ['This field is required.'])

	def test_save_CatalogFormRemove_valid_form(self):
		form = CatalogFormRemove(data={'parent': self.catalog.pk})
		self.assertTrue(form.is_valid())
		self.assertIn(self.catalog, Catalog.objects.all())
		form.save()
		self.assertNotIn(self.catalog, Catalog.objects.all())

	def test_save_CatalogFormRemove_invalid_form(self):
		form = CatalogFormRemove(data={'parent': -1})
		self.assertFalse(form.is_valid())
		with self.assertRaises(KeyError):
			form.save()
		self.assertIn(self.catalog, Catalog.objects.all())

	def test_save_ItemFormAdd_valid_form(self):
		form = ItemFormAdd(data={'name': 'Item 2',
								 'catalog': self.catalog.pk,
								 'description': '...',
								 'link': 'www.example.com'})
		self.assertTrue(form.is_valid())
		item_instance = form.save()
		self.assertIn(item_instance, Item.objects.all())

	def test_save_ItemFormAdd_invalid_form(self):
		form = ItemFormAdd(data={'name': 'Item 1',
								 'link': 'com',
								 'description': '...',
								 'catalog': -1})
		self.assertFalse(form.is_valid())
		with self.assertRaises(ValueError):
			form.save()

		self.assertEqual(form.errors['name'],
						 ['Item with this Name already exists.'])
		self.assertEqual(form.errors['link'],
						 ['Enter a valid URL.'])
		self.assertEqual(form.errors['catalog'],
						 ['Select a valid choice. That choice is not one of the available choices.'])

	def test_ItemFormAdd_form_validation_for_invalid_link(self):
		form = ItemFormAdd(data={'name': 'Item 2',
								 'catalog': self.catalog.pk,
								 'link': 'invalid_link'})
		self.assertFalse(form.is_valid())
		self.assertEqual(form.errors['description'], ['This field is required.'])
		self.assertEqual(form.errors['link'], ['Enter a valid URL.'])

	def test_save_ItemFormRemove_valid_form(self):
		form = ItemFormRemove(data={'item': self.item.pk})
		self.assertTrue(form.is_valid())
		self.assertIn(self.item, Item.objects.all())
		form.save()
		self.assertNotIn(self.item, Item.objects.all())

	def test_save_ItemFormRemove_invalid_form(self):
		form = ItemFormRemove(data={'item': -1})
		self.assertFalse(form.is_valid())
		with self.assertRaises(KeyError):
			form.save()
		self.assertIn(self.item, Item.objects.all())


class ViewTest(TestCase):

	def setUp(self):
		self.catalog = Catalog.objects.create(name='Root')
		self.item = Item.objects.create(name='Item 1', catalog=self.catalog)

	def test_tree_traversal_page_uses_correct_view(self):
		response = self.client.get(reverse('tree_traversal:tree_traversal'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.resolver_match.func, tree_traversal)

	def test_tree_traversal_page_render_correct_template(self):
		response = self.client.get(reverse('tree_traversal:tree_traversal'))

		self.assertTemplateUsed(response, 'tree_traversal/home.html')

	def test_tree_traversal_page_uses_correct_forms(self):
		response = self.client.get(reverse('tree_traversal:tree_traversal'))

		self.assertIsInstance(response.context['catalog_form_add'], CatalogFormAdd)
		self.assertIsInstance(response.context['catalog_form_remove'], CatalogFormRemove)
		self.assertIsInstance(response.context['item_form_add'], ItemFormAdd)
		self.assertIsInstance(response.context['item_form_remove'], ItemFormRemove)

	def test_tree_traversal_add_catalog_POST_valid_request(self):
		response = self.client.post(
			reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			# content_type='application/json',
			data={'catalog_form_add-name': 'Documents',
				  'catalog_form_add-parent': self.catalog.pk,
				  'form_name': 'catalog_form_add'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('Documents', Catalog.objects.values_list('name', flat=True))
		self.assertContains(response, 'Documents')

	def test_tree_traversal_add_catalog_POST_invalid_request(self):
		response = self.client.post(
			reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'catalog_form_add-name': 'Root',
				  'form_name': 'catalog_form_add'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['catalog_form_add'].errors['name'],
						 ['Catalog with this Name already exists.'])

	def test_tree_traversal_remove_catalog_POST_valid_request(self):
		self.assertIn(self.catalog, Catalog.objects.all())
		response = self.client.post(
			reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'catalog_form_remove-parent': self.catalog.pk,
				  'form_name': 'catalog_form_remove'})

		self.assertEqual(response.status_code, 200)
		self.assertNotIn(self.catalog, Catalog.objects.all())
		self.assertNotContains(response, self.catalog.name)

	def test_tree_traversal_remove_catalog_POST_invalid_request(self):
		response = self.client.post(
			reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'catalog_form_remove-parent': -1,
				  'form_name': 'catalog_form_remove'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['catalog_form_remove'].errors['parent'],
						 ['Select a valid choice. That choice is not one of the available choices.'])

	def test_tree_traversal_add_item_POST_valid_request(self):
		response = self.client.post(
			reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'item_form_add-name': 'Item 2',
				  'item_form_add-description': '...',
				  'item_form_add-catalog': self.catalog.pk,
				  'form_name': 'item_form_add'})

		self.assertEqual(response.status_code, 200)
		self.assertIn('Item 2', Item.objects.values_list('name', flat=True))
		self.assertContains(response, 'Item 2')

	def test_tree_traversal_add_item_POST_invalid_request(self):
		response = self.client.post(
			reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'item_form_add-name': 'Item 1',
				  'item_form_add-link': 'com',
				  'item_form_add-description': '...',
				  'item_form_add-catalog': -1,
				  'form_name': 'item_form_add'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['item_form_add'].errors['name'],
						 ['Item with this Name already exists.'])
		self.assertEqual(response.context['item_form_add'].errors['link'],
						 ['Enter a valid URL.'])
		self.assertEqual(response.context['item_form_add'].errors['catalog'],
						 ['Select a valid choice. That choice is not one of the available choices.'])

	def test_tree_traversal_remove_item_POST_valid_request(self):
		self.assertIn(self.item, Item.objects.all())

		response = self.client.post(reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'item_form_remove-item': self.item.pk,
				  'form_name': 'item_form_remove'})

		self.assertEqual(response.status_code, 200)
		self.assertNotIn(self.item, Item.objects.all())
		self.assertNotContains(response, self.item.name)

	def test_tree_traversal_remove_item_POST_invalid_request(self):
		response = self.client.post(reverse('tree_traversal:tree_traversal'),
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			data={'item_form_remove-item': -1,
				  'form_name': 'item_form_remove'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['item_form_remove'].errors['item'],
						 ['Select a valid choice. That choice is not one of the available choices.'])
