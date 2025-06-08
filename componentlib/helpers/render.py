import importlib
import json
from pathlib import Path

def render_component(key: str, kwargs: dict = None) -> str:
    try:
        # Find the path to the component folder
        base_path = Path(__file__).resolve().parent.parent / "components" / key

        # Dynamically import the Python module
        module_path = f"componentlib.components.{key}.component"
        module = importlib.import_module(module_path)

        # Find the class that ends with "Component"
        class_name = next(name for name in dir(module) if name.endswith("Component"))
        cls = getattr(module, class_name)

        # Use kwargs if provided, otherwise read example.json
        if not kwargs:
            example_path = base_path / "example.json"
            if example_path.exists():
                with open(example_path, "r") as f:
                    kwargs = json.load(f)
            else:
                kwargs = {}

        # Instantiate and render the component
        instance = cls(**kwargs)
        return instance.render()

    except Exception as e:
        # Return an error message if something goes wrong
        return f"<em>Error in component '{key}': {e}</em>"
