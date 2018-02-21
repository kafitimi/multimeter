""" Кастомные фильтры """

from django import template
from django.forms import CheckboxInput

register = template.Library()


@register.filter
def form_control(field):
    """ Добавляет классы form-control и is-invalid к виджету поля формы для работы с Bootstrap """
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
    """ Добавляет класс form-check-input к виджету поля формы для работы с Bootstrap """
    attributes = field.field.widget.attrs
    if 'class' not in attributes:
        attributes['class'] = ''

    class3 = 'form-check-input'
    if class3 not in attributes['class']:
        attributes['class'] += ' ' + class3

    attributes['class'] = attributes['class'].strip()
    return field


@register.filter
def set_placeholder(field, text):
    """ Устанавливает атрибут placeholder у виджета поля формы """
    attributes = field.field.widget.attrs
    attributes['placeholder'] = text
    return field


@register.filter
def is_boolean(field):
    """ Проверяет является ли виджет поля формы чекбоксом или нет """
    return isinstance(field.field.widget, CheckboxInput)
