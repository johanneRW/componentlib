import importlib
from django import template
from componentlib.helpers.render import render_component  # your existing helper
import html

register = template.Library()

@register.simple_tag(takes_context=True)
def render_component_tag(context, name, **kwargs):
    """
    Usage: {% render_component_tag "name" key1=value1 key2=value2 %}
    """
    try:
        rendered = render_component(name, kwargs)
        return rendered  # already safe HTML
    except Exception as e:
        return f"<em>Error in component '{name}': {html.escape(str(e))}</em>"


def get_component_class(key):
    try:
        mod = importlib.import_module(f"componentlib.components.{key}.component")
        class_name = [name for name in dir(mod) if name.endswith("Component")][0]
        return getattr(mod, class_name)
    except Exception as e:
        return None
