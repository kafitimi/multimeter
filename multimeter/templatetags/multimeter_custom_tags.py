from django import template

register = template.Library()


@register.filter
def form_control(field):
    addition = 'form-control'
    attributes = field.field.widget.attrs
    if 'class' in attributes:
        if addition not in attributes['class']:
            attributes['class'] += ' ' + addition
    else:
        attributes['class'] = addition
    return field
