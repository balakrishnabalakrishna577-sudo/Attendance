"""
Custom template filters for the attendance app.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Usage: {{ my_dict|get_item:key_variable }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


@register.filter
def percentage_color(value):
    """Return a CSS color class based on attendance percentage."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ''
    if v >= 75:
        return 'text-success-custom'
    elif v >= 50:
        return ''  # warning color inline in template
    return 'text-danger-custom'
