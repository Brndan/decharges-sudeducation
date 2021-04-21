from django import template

register = template.Library()


@register.filter
def index(array, i):
    return array[i]
