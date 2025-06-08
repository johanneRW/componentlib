import importlib
import json
import inspect
from pathlib import Path

def render_component_preview(component_key: str) -> str:
    try:
        module_path = f"componentlib.components.{component_key}.component"

        # Dynamically import the module
        module = importlib.import_module(module_path)
        component_classes = [
            obj for name, obj in inspect.getmembers(module, inspect.isclass)
            if name.endswith("Component") and obj.__module__ == module.__name__
        ]

        # Use the first matching class
        cls = component_classes[0]

        # Resolve the base path for the component
        base_path = Path(module.__file__).resolve().parent

        # Load example data from example.json if it exists
        example_path = base_path / "example.json"
        kwargs = {}
        if example_path.exists():
            with open(example_path, "r") as f:
                kwargs = json.load(f)

        # Create an instance of the component and render it
        instance = cls(base_path=base_path, **kwargs)
        return instance.render()

    except Exception as e:
        # Return an error message if something goes wrong
        return f"<em>Error in component '{component_key}': {e}</em>"



