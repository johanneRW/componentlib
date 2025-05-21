import importlib
import json
import inspect
from pathlib import Path

def render_component_preview(component_key: str) -> str:
    try:
        module_path = f"componentlib.components.{component_key}.component"
        print("[PREVIEW] trying to import:", module_path)

        module = importlib.import_module(module_path)
        component_classes = [
            obj for name, obj in inspect.getmembers(module, inspect.isclass)
            if name.endswith("Component") and obj.__module__ == module.__name__
        ]

        cls = component_classes[0]  # Brug første match
        print("[RENDER PREVIEW] Using class:", cls.__name__)


        base_path = Path(module.__file__).resolve().parent
        print("[PREVIEW] base_path:", base_path)

        example_path = base_path / "example.json"
        kwargs = {}
        if example_path.exists():
            with open(example_path, "r") as f:
                kwargs = json.load(f)
        print("[PREVIEW] example kwargs:", kwargs)

        instance = cls(base_path=base_path, **kwargs)
        return instance.render()

    except Exception as e:
        print("[PREVIEW ERROR]", e)  # <<< vigtig linje
        return f"<em>Fejl i komponent '{component_key}': {e}</em>"



