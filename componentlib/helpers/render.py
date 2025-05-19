import importlib
import json
from pathlib import Path

def render_component(key: str, kwargs: dict = None) -> str:
    try:
        # Find stien til komponentmappen
        base_path = Path(__file__).resolve().parent.parent / "components" / key

        # Importer Python-modulet dynamisk
        module_path = f"componentlib.components.{key}.component"
        module = importlib.import_module(module_path)

        # Find den klasse der ender på "Component"
        class_name = next(name for name in dir(module) if name.endswith("Component"))
        cls = getattr(module, class_name)

        # Brug kwargs hvis de gives, ellers læs example.json
        if not kwargs:
            example_path = base_path / "example.json"
            if example_path.exists():
                with open(example_path, "r") as f:
                    kwargs = json.load(f)
            else:
                kwargs = {}

        # Instantiér og render komponenten
        instance = cls(**kwargs)
        return instance.render()

    except Exception as e:
        return f"<em>Fejl i komponent '{key}': {e}</em>"
