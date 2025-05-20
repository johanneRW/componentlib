import yaml
import warnings
from pathlib import Path
from django.template import engines




class BaseComponent:
    template_filename = "template.html"
    metadata_filename = "metadata.yaml"

    def __init__(self, **kwargs):
        self.context = kwargs
        self.base_path = Path(__file__).resolve().parent
        self.metadata = self.load_metadata()
        self.validate_context()

    def load_metadata(self) -> dict:
        meta_path = self.base_path / self.metadata_filename
        if not meta_path.exists():
            return {}

        with open(meta_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


    def validate_context(self):
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "list": list,
            "dict": dict,
        }

        inputs = self.metadata.get("inputs", {})
        for key, info in inputs.items():
            # Tilføj default hvis ikke givet
            if key not in self.context and "default" in info:
                self.context[key] = info["default"]

            # Hvis stadig ikke i context og required
            if info.get("required", False) and key not in self.context:
                warnings.warn(f"[Component] Missing required input: '{key}'")

            # Type check
            expected_type = info.get("type")
            if expected_type and key in self.context:
                val = self.context[key]
                python_type = type_map.get(expected_type)

                if python_type and not isinstance(val, python_type):
                    warnings.warn(f"[Component] '{key}' should be of type '{expected_type}', got {type(val).__name__}")



    def get_context_data(self) -> dict:
        return self.context  # kan overskrives i subklasse

    def render(self) -> str:
        template_path = self.base_path / self.template_filename
        template_string = template_path.read_text(encoding="utf-8")
        django_engine = engines["django"]
        template = django_engine.from_string(template_string)
        return template.render(self.get_context_data())
