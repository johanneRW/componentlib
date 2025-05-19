import importlib.util
from pathlib import Path
import os

COMPONENTS_DIR = Path(__file__).resolve().parent / "components"

class Component:
    def __init__(self, name):
        self.name = name
        self.dir = COMPONENTS_DIR / name

        self.template_path = self.dir / "template.html"
        self.module = self._load_py()

    def _load_py(self):
        py_path = self.dir / "component.py"
        if not py_path.exists():
            return None
        spec = importlib.util.spec_from_file_location(f"{self.name}_component", py_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

def get_component(name):
    return Component(name)

def component_template(name):
    """Return Django-style template path as string"""
    return f"components/{name}/template.html"
