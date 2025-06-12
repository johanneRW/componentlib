import importlib
import inspect
import json
from pathlib import Path

from django.template import engines, TemplateSyntaxError
from django.test.client import RequestFactory
from django.conf import settings
from django.utils.translation import get_language

from componentlib.helpers.registry import load_all_components


def render_component_preview(component_key: str) -> str:
    try:
        module_path = f"componentlib.components.{component_key}.component"
        base_path = Path(__file__).resolve().parent.parent / "components" / component_key
        example_path = base_path / "example.json"
        kwargs = {}

        # Load example.json if available
        if example_path.exists():
            try:
                with open(example_path, "r", encoding="utf-8") as f:
                    kwargs = json.load(f)
            except json.JSONDecodeError as e:
                return f"<em>Invalid JSON in example.json for '{component_key}': {e}</em>"

        # Patch in dummy request and language context
        request = RequestFactory().get("/")
        kwargs["request"] = request
        kwargs["LANGUAGES"] = settings.LANGUAGES
        kwargs["LANGUAGE_CODE"] = get_language()

        # Patch in dummy form object if 'form' is present as a dict
        if "form" in kwargs and isinstance(kwargs["form"], dict):
            class DummyForm:
                def __init__(self, data):
                    self.status = data.get("status", "DRAFT")
                def get_status_display(self):
                    return self.status.capitalize()
            kwargs["form"] = DummyForm(kwargs["form"])

        # Try to render via component class
        try:
            module = importlib.import_module(module_path)
            component_classes = [
                obj for name, obj in inspect.getmembers(module, inspect.isclass)
                if name.endswith("Component") and obj.__module__ == module.__name__
            ]
            cls = component_classes[0]
            instance = cls(base_path=base_path, **kwargs)
            return instance.render()

        except ModuleNotFoundError:
            # No component.py — fall back to template.html
            template_path = base_path / "template.html"
            if not template_path.exists():
                return f"<em>No template.html found for '{component_key}'</em>"

            template_string = template_path.read_text(encoding="utf-8")
            django_engine = engines["django"]
            template = django_engine.from_string(template_string)

            try:
                return template.render(kwargs)
            except TemplateSyntaxError as e:
                return f"<em>Template error in '{component_key}': {e}</em>"

    except Exception as e:
        return f"<em>Error in component '{component_key}': {e}</em>"


def load_and_render_components():
    all_components = load_all_components()
    for c in all_components:
        c["rendered"] = render_component_preview(c["key"])
    return all_components