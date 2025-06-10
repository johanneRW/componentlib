import json
import yaml
from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Generates props.py based on example.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "component",
            nargs="?",
            default=None,
            help="(Optional) Name of the component folder – otherwise runs for all"
        )

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / "components"
        only = options.get("component")

        if only:
            component_dirs = [base_dir / only]
        else:
            component_dirs = [d for d in base_dir.iterdir() if d.is_dir()]

        for component_dir in component_dirs:
            if not component_dir.exists():
                self.stdout.write(self.style.ERROR(f"[✗] The folder '{component_dir}' does not exist."))
                continue

            example_path = component_dir / "example.json"
            if not example_path.exists():
                self.stdout.write(self.style.WARNING(f"[SKIP] {component_dir.name} (no example.json)"))
                continue

            with open(example_path, "r", encoding="utf-8") as f:
                example_data = json.load(f)

            self.generate_props_from_example(component_dir, example_data)

    def generate_props_from_example(self, component_dir: Path, example_data: dict):
        class_name = component_dir.name.title().replace("-", "").replace("_", "") + "ComponentProps"
        metadata_path = component_dir / "metadata.yaml"
        metadata = {}

        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)

        inputs = metadata.get("inputs", {})

        used_types = defaultdict(bool)
        fields = []

        def map_type(meta_type):
            if meta_type == "string":
                return "str"
            elif meta_type == "boolean":
                return "bool"
            elif meta_type == "number":
                return "float"
            elif meta_type == "list":
                used_types["List"] = True
                return "List[Any]"
            elif meta_type == "dict":
                used_types["Dict"] = True
                return "Dict[str, Any]"
            else:
                used_types["Any"] = True
                return "Any"

        for key, config in inputs.items():
            meta_type = config.get("type", "string")
            required = config.get("required", False)
            default = config.get("default", None)

            py_type = map_type(meta_type)

            if not required:
                used_types["Optional"] = True
                py_type = f"Optional[{py_type}]"

            if default is None:
                used_types["Any"] = True
                default_repr = "None"
            else:
                default_repr = repr(default)

            fields.append(f"    {key}: {py_type} = Field({default_repr})")

        # Imports
        typing_imports = [k for k, v in used_types.items() if v]
        typing_line = f"from typing import {', '.join(sorted(typing_imports))}" if typing_imports else ""

        lines = [
            f'__all__ = ["{class_name}"]\n',
            "from pydantic import BaseModel, Field",
        ]

        if typing_line:
            lines.append(typing_line)

        lines.append("")
        lines.append(f"class {class_name}(BaseModel):")

        if fields:
            lines.extend(fields)
        else:
            lines.append("    pass")

        output_path = component_dir / "props.py"
        new_content = "\n".join(lines) + "\n"

        if output_path.exists() and output_path.read_text(encoding="utf-8") == new_content:
            self.stdout.write(self.style.NOTICE(f"[=] {component_dir.name}/props.py unchanged"))
        else:
            output_path.write_text(new_content, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[✔] {component_dir.name}/props.py updated"))

