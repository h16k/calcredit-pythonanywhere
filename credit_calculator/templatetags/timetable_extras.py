from django import template

register = template.Library()

@register.filter
def lookup(value, arg):
    return value.get(arg)

@register.filter
def make_list(value):
    return list(value)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
