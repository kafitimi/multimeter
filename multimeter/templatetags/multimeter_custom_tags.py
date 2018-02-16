from django import template
from django.forms import CheckboxInput

register = template.Library()


@register.filter
def form_control(field):
    attributes = field.field.widget.attrs
    if 'class' not in attributes:
        attributes['class'] = ''

    class1 = 'form-control'
    if class1 not in attributes['class']:
        attributes['class'] += ' ' + class1

    class2 = 'is-invalid'
    if field.errors and class2 not in attributes['class']:
        attributes['class'] += ' ' + class2

    attributes['class'] = attributes['class'].strip()
    return field


@register.filter
def form_check_input(field):
    attributes = field.field.widget.attrs
    if 'class' not in attributes:
        attributes['class'] = ''

    class3 = 'form-check-input'
    if class3 not in attributes['class']:
        attributes['class'] += ' ' + class3

    attributes['class'] = attributes['class'].strip()
    return field


@register.filter
def is_boolean(field):
    return isinstance(field.field.widget, CheckboxInput)
