from django import template

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
