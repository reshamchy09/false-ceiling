from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to get dictionary value by key
    Usage: {{ dict|lookup:key }}
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    try:
        return dictionary[key]
    except (KeyError, TypeError, AttributeError):
        return None