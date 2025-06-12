import yaml
import importlib
import inspect
from pathlib import Path
from .htmx_detect import detect_component_capabilities


# Internal storage for registered component classes
_component_classes = {}

def load_all_components():
    base_path = Path(__file__).resolve().parent.parent / "components"
    components = []

    for comp_dir in base_path.iterdir():
        meta_file = comp_dir / "metadata.yaml"
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                data["key"] = comp_dir.name

                # Check for existing files
                data["exists"] = {
                    "component_py": (comp_dir / "component.py").exists(),
                    "template_html": (comp_dir / "template.html").exists(),
                    "metadata_yaml": meta_file.exists(),
                    "readme_md": (comp_dir / "README.md").exists(),
                    "example_json": (comp_dir / "example.json").exists(),
                }

                # Metadata tags from YAML
                metadata_tags = data.get("tags", [])
                data["tags"] = metadata_tags  # ← only user-defined tags

                # Detect capabilities
                template_file = comp_dir / "template.html"
                capabilities = detect_component_capabilities(template_file)
                data["capabilities"] = capabilities  # also store raw capabilities

                # Build system technologies
                system_technologies = []
                if data["exists"]["component_py"]:
                    system_technologies.append("django")
                if capabilities["has_htmx"]:
                    system_technologies.append("htmx")
                elif capabilities["has_simple_html"]:
                    system_technologies.append("html")

                data["technologies"] = system_technologies  # ← system tags stored here

                # Attempt to import the component class
                try:
                    module_path = f"componentlib.components.{comp_dir.name}.component"
                    module = importlib.import_module(module_path)

                    component_classes = [
                        obj for name, obj in inspect.getmembers(module, inspect.isclass)
                        if name.endswith("Component") and obj.__module__ == module.__name__
                    ]

                    if component_classes:
                        cls = component_classes[0]
                        data["class_name"] = cls.__name__
                        _component_classes[comp_dir.name] = cls
                    else:
                        data["class_name"] = None
                        data["import_error"] = "No class ending in 'Component' found"

                except Exception as e:
                    data["class_name"] = None
                    data["import_error"] = str(e)

                components.append(data)

    return components


def get_component_class(name):
    """Retrieve component class based on folder name (key)"""
    return _component_classes.get(name)

