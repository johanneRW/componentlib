import yaml
import inspect
from pathlib import Path
from django.template import engines

class BaseComponent:
    template_filename = "template.html"
    metadata_filename = "metadata.yaml"

    def __init__(self, base_path=None, **kwargs):
        self.base_path = Path(base_path) if base_path else Path(inspect.getfile(self.__class__)).resolve().parent
        self.metadata = self.load_metadata()

        # Internal context
        self.context = kwargs.copy()

        # Insert dynamic fields before rendering
        self.apply_dynamic_fields()

        # Warn if props are not used
        if not getattr(self, "_validated", False):
            print(f"[WARNING] ⚠️  {self.__class__.__name__} input not validated via Props model.")

    def load_metadata(self) -> dict:
        meta_path = self.base_path / self.metadata_filename
        if not meta_path.exists():
            return {}
        with open(meta_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def resolve_path(self, context, dotted_path: str):
        try:
            for part in dotted_path.split("."):
                context = getattr(context, part, None)
            return context
        except Exception:
            return None

    def apply_dynamic_fields(self):
        """
        Check for fields like value_from / disabled_from, etc.,
        and insert them into the context if they are missing.
        """
        form = self.context.get("form") or self.context.get("context")

        for key in list(self.context.keys()):
            if key.endswith("_from") and isinstance(self.context[key], str):
                target_key = key.replace("_from", "")
                if target_key not in self.context:
                    path = self.context[key]
                    self.context[target_key] = self.resolve_path(form, path)

    def get_context_data(self) -> dict:
        return self.context

    def render(self) -> str:
        template_path = self.base_path / self.template_filename
        template_string = template_path.read_text(encoding="utf-8")
        django_engine = engines["django"]
        template = django_engine.from_string(template_string)
        return template.render(self.get_context_data())
