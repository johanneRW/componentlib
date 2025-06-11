import json
import re
import difflib
from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates props.py based on example.json and template.html (with optional type/default comments)"

    def add_arguments(self, parser):
        parser.add_argument(
            "component",
            nargs="?",
            default=None,
            help="(Optional) Name of the component folder – otherwise runs for all"
        )

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / "components"
        component_name = options.get("component")
        all_components = [d.name for d in base_dir.iterdir() if d.is_dir()]

        if component_name:
            target_path = base_dir / component_name
            if not target_path.exists():
                suggestions = difflib.get_close_matches(component_name, all_components, n=3)
                suggestion_text = f"\nDid you mean: {', '.join(suggestions)}?" if suggestions else ""
                self.stdout.write(self.style.ERROR(f"[✗] Component '{component_name}' not found.{suggestion_text}"))
                return
            component_dirs = [target_path]
        else:
            component_dirs = [base_dir / name for name in all_components]

        for component_dir in component_dirs:
            self.stdout.write(self.style.HTTP_INFO(f"[~] Updating: {component_dir.name}"))
            self.generate_props(component_dir)

    def generate_props(self, component_dir: Path):
        class_name = component_dir.name.title().replace("-", "").replace("_", "") + "ComponentProps"
        example_path = component_dir / "example.json"
        template_path = component_dir / "template.html"
        output_path = component_dir / "props.py"

        props = {}
        used_types = defaultdict(bool)

        # 1. Load from example.json
        if example_path.exists():
            with open(example_path, "r", encoding="utf-8") as f:
                example_data = json.load(f)
                for key, value in example_data.items():
                    props[key] = {
                        "type": self.guess_type(value),
                        "default": value,
                    }

        # 2. Load from template.html with optional type/default comments
        if template_path.exists():
            template_text = template_path.read_text(encoding="utf-8")
            matches = re.findall(
                r"\{\{\s*props\.(\w+)\s*\}\}(?:\s*<!--\s*type:\s*(\w+)(?:,\s*default:\s*(.+?))?\s*-->)?",
                template_text
            )
            for key, typ, default in matches:
                if key in props:
                    continue  # skip if already defined via JSON
                inferred_type = typ if typ else "string"
                parsed_default = None
                if default:
                    try:
                        parsed_default = json.loads(default)
                    except Exception:
                        parsed_default = default.strip('"\'')
                props[key] = {
                    "type": inferred_type,
                    "default": parsed_default,
                }

        # 3. Map types and prepare fields
        def map_type(prop_type):
            if prop_type == "string":
                return "str"
            elif prop_type == "boolean":
                return "bool"
            elif prop_type == "number":
                return "float"
            elif prop_type == "list":
                used_types["List"] = True
                used_types["Any"] = True
                return "List[Any]"
            elif prop_type == "dict":
                used_types["Dict"] = True
                used_types["Any"] = True
                return "Dict[str, Any]"
            else:
                used_types["Any"] = True
                return "Any"


        fields = []
        for key in sorted(props.keys()):
            info = props[key]
            py_type = map_type(info["type"])
            used_types["Optional"] = True
            py_type = f"Optional[{py_type}]"
            if info["default"] is None:
                default_repr = "None"
            elif isinstance(info["default"], (list, dict)):
                default_repr = "..."  # Avoid hardcoded example values
            else:
                default_repr = repr(info["default"])

            fields.append(f"    {key}: {py_type} = Field({default_repr})")

        # 4. Build file contents
        typing_imports = [k for k, v in used_types.items() if v]
        typing_line = f"from typing import {', '.join(sorted(typing_imports))}" if typing_imports else ""

        note_lines = [
            "# NOTE: This file is auto-generated.",
            "# To update it, run: `python manage.py update_props <component_name>`",
            "# The generation is based on template.html and example.json.",
            "# Fields can include type/default using HTML comments:",
            "#    {{ props.name }} <!-- type: string, default: \"John\" -->",
            "# Please verify that all fields are correctly merged and validated.",
            "",
        ]

        lines = note_lines + [
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

        new_content = "\n".join(lines) + "\n"

        # 5. Write only if changed
        if output_path.exists() and output_path.read_text(encoding="utf-8") == new_content:
            self.stdout.write(self.style.NOTICE(f"[=] {component_dir.name}/props.py unchanged"))
        else:
            output_path.write_text(new_content, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[✔] {component_dir.name}/props.py updated"))

    def guess_type(self, value):
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "string"
