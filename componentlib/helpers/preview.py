import importlib
import json
from pathlib import Path

def render_component_preview(component_key: str) -> str:
    try:
        base_path = Path(__file__).resolve().parent.parent / "components" / component_key
        module = importlib.import_module(f"componentlib.components.{component_key}.component")
        class_name = [name for name in dir(module) if name.endswith("Component")][0]
        cls = getattr(module, class_name)

        example_path = base_path / "example.json"
        kwargs = {}
        if example_path.exists():
            with open(example_path, "r") as f:
                kwargs = json.load(f)

        instance = cls(**kwargs)
        return instance.render()

    except Exception as e:
        return f"<em>Fejl i komponent '{component_key}': {e}</em>"
