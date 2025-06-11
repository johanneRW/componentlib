from django import template

register = template.Library()

@register.filter
def exclude(value, item):
    return [v for v in value if v != item]


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")


@register.filter
def tech_options(tech_list):
    return [[t, t.capitalize()] for t in tech_list]