from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def attr_list(obj):
	'''
	In templates
	{% load utility_tags %}
	{% attr_list object_to_inspect %}
	'''
	html = ''
	for item in dir(obj):
		if not item.startswith('__'):
			html += '<p>{0}</p>'.format(item)
	return mark_safe(html)


@register.simple_tag
def form_field(field, *args, **kwargs):
	'''
	In templates
	{% load utility_tags %}
	{% form_field form.field_name %}
	'''
	template = 'forms/form_field.html'
	ctx = {
		'field': field,
	}

	field_type = field.field.widget.__class__.__name__

	if field_type in ('TextInput', 'NumberInput', 'URLInput', 'PasswordInput'):
		# Additional kwargs: 'affix_addon'
		if 'affix_addon' in kwargs:
			ctx['affix_addon'] = kwargs.get('affix_addon', None)
		ctx['input_type'] = field.field.widget.input_type
	elif field_type in ('Textarea', ):
		ctx['textarea'] = True
	elif field_type in ('Select', ):
		ctx['select'] = True
	elif field_type in ('CheckboxInput', ):
		# Additional kwargs: 'checkbox_text'
		ctx['checkbox'] = True
		ctx['checkbox_text'] = kwargs.get('checkbox_text', None)
	elif field_type in ('RadioSelect', ):
		ctx['radio_input'] = True
	elif field_type in ('ClearableFileInput', ):
		ctx['file_input'] = True

	return mark_safe(render_to_string(template, ctx))
