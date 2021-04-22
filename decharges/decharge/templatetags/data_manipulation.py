from django import template

register = template.Library()


@register.filter
def index(array, i):
    return array[i]


@register.filter(name="abs")
def abs_filter(value):
    return abs(value)
