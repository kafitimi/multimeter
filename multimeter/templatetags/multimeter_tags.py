from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def form_control(bound_field):
    attributes = bound_field.field.widget.attrs
    classes = attributes['class'].split() if 'class' in attributes else []
    if 'form-control' not in classes:
        classes.append('form-control')
    if bound_field.errors and 'is-invalid' not in classes:
        classes.append('is-invalid')
    attributes['class'] = ' '.join(classes)
    return bound_field


@register.inclusion_tag('multimeter/form_control.html')
def form_control(form_field: BoundField, col: str = '') -> dict:
    """
    Делаем бутстраповский форм-контрол из джанговского поля формы
    Фичи:
    - если после валидации нашлись косяки, показываем их
    - если в поле есть хелп-текст, то показываем его
    - опционально передаем в form-group CSS-класс для выстраивания полей в грид (например col, col-3 и т.п.)
    """

    # Если в форме нет такого поля, то нужно сообщить об этом куда следует
    try:
        attributes = form_field.field.widget.attrs
    except AttributeError as e:
        print('Form does not have such field: %s' % str(form_field))
        raise e

    # Список CSS-классов оформления, который нужно навесить на тег input
    css_classes = ['form-control']

    # Подсветим красненьким косячные поля
    if form_field.errors:
        css_classes.append('is-invalid')

    # Сохраним имеющиеся CSS-классы оформления
    if 'class' in attributes:
        css_classes.append(attributes['class'])

    attributes['class'] = ' '.join(css_classes)
    return {'col': col, 'form_field': form_field, 'help': str(form_field.help_text)}


@register.inclusion_tag('multimeter/form_check.html')
def form_check(form_field: BoundField, col: str = '') -> dict:
    """
    Делаем бутстраповский чекбокс из джанговского поля формы
    Фичи:
    - если после валидации нашлись косяки, показываем их
    - если в поле есть хелп-текст, то показываем его
    - опционально передаем в form-group CSS-класс для выстраивания полей в грид (например col, col-3 и т.п.)
    """

    # Если в форме нет такого поля, то нужно сообщить об этом куда следует
    try:
        attributes = form_field.field.widget.attrs
    except AttributeError as e:
        print('Form does not have such field: %s' % str(form_field))
        raise e

    # Список CSS-классов оформления, который нужно навесить на тег input
    css_classes = ['form-check-input']

    # Подсветим красненьким косячные поля
    if form_field.errors:
        css_classes.append('is-invalid')

    # Сохраним имеющиеся CSS-классы оформления
    if 'class' in attributes:
        css_classes.append(attributes['class'])

    attributes['class'] = ' '.join(css_classes)
    return {'col': col, 'form_field': form_field, 'help': str(form_field.help_text)}
