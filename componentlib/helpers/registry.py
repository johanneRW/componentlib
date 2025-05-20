import yaml
import importlib
import inspect
from pathlib import Path

def load_all_components_metadata():
    base_path = Path(__file__).resolve().parent.parent / "components"
    components = []

    for comp_dir in base_path.iterdir():
        meta_file = comp_dir / "metadata.yaml"
        if meta_file.exists():
            with open(meta_file, "r") as f:
                data = yaml.safe_load(f)
                data["key"] = comp_dir.name
                # Tilføj komponent-eksistens-status
                data["exists"] = {
                    "component_py": (comp_dir / "component.py").exists(),
                    "template_html": (comp_dir / "template.html").exists(),
                    "metadata_yaml": meta_file.exists(),
                    "readme_md": (comp_dir / "README.md").exists(),
                    "example_json": (comp_dir / "example.json").exists(),
                    "example_html": (comp_dir / "example.html").exists(),
                }
#TODO: fjern evt scoren, hvis den ikke bliver brugt længere
                # Beregn dokumentations-score
                documentation_parts = [
                    "metadata_yaml",
                    "readme_md",
                    "example_json",
                    "example_html",
                ]
                exists = data["exists"]
                documentation_score = sum(1 for part in documentation_parts if exists.get(part, False))

                # Tjek om mindst en af de kritiske filer (.py eller .html) eksisterer
                critical_files_exist = exists["component_py"] or exists["template_html"]
                critical_files_count = sum(1 for part in ["component_py", "template_html"] if exists.get(part, False))

                data["completeness"] = {
                    "documentation_score": documentation_score,
                    "documentation_total": len(documentation_parts),
                    "critical_files_count": critical_files_count,
                    "critical_files_total": 2,
                }

                try:
                    module_path = f"componentlib.components.{comp_dir.name}.component"
                    module = importlib.import_module(module_path)

                    # Find klasser der ender på 'Component' og er defineret i dette modul (ikke importerede)
                    component_classes = [
                        obj for name, obj in inspect.getmembers(module, inspect.isclass)
                        if name.endswith("Component") and obj.__module__ == module.__name__
                    ]

                    if component_classes:
                        cls = component_classes[0]
                        data["class_name"] = cls.__name__
                    else:
                        data["class_name"] = None  # eller evt. en fejlmarkering

                except Exception as e:
                    data["import_error"] = str(e)

                components.append(data)

    return components
