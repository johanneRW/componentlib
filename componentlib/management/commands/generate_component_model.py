import json
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
        from collections import defaultdict

        class_name = component_dir.name.title().replace("-", "").replace("_", "") + "ComponentProps"
        used_types = defaultdict(bool)

        def infer_type(value):
            # Handle None
            if value is None:
                used_types["Optional"] = True
                used_types["Any"] = True
                return "Optional[Any]"

            # Handle strings, numbers, bool
            if isinstance(value, str):
                return "str"
            if isinstance(value, bool):
                return "bool"
            if isinstance(value, int):
                return "int"
            if isinstance(value, float):
                return "float"

            # Handle list values
            if isinstance(value, list):
                used_types["List"] = True

                # Literal if simple, short list of primitive values
                if all(isinstance(v, (str, int, float, bool)) for v in value) and len(set(value)) <= 10:
                    used_types["Literal"] = True
                    literals = ", ".join(repr(v) for v in sorted(set(value)))
                    return f"Literal[{literals}]"

                # Tuple[str, str] for list of 2-element lists
                if all(isinstance(i, list) and len(i) == 2 and all(isinstance(j, str) for j in i) for i in value):
                    used_types["Tuple"] = True
                    return "List[Tuple[str, str]]"

                return "List[Any]"

            # Handle dict
            if isinstance(value, dict):
                used_types["Dict"] = True
                return "Dict[str, Any]"

            # Default fallback
            used_types["Any"] = True
            return "Any"

        # Header and imports
        lines = [
            f'__all__ = ["{class_name}"]\n',
            "from pydantic import BaseModel, Field"
        ]

        # Build fields
        fields = []
        for key, value in example_data.items():
            inferred_type = infer_type(value)
            default_repr = repr(value)
            fields.append(f"    {key}: {inferred_type} = Field({default_repr})")

        # Build typing import line dynamically
        typing_imports = ", ".join(sorted(k for k, v in used_types.items() if v))
        if typing_imports:
            lines.append(f"from typing import {typing_imports}\n")
        else:
            lines.append("")  # for spacing

        # Class header
        lines.append(f"class {class_name}(BaseModel):")
        if fields:
            lines.extend(fields)
        else:
            lines.append("    pass")

        # Write to file
        output_path = component_dir / "props.py"
        new_content = "\n".join(lines) + "\n"

        if output_path.exists() and output_path.read_text(encoding="utf-8") == new_content:
            self.stdout.write(self.style.NOTICE(f"[=] {component_dir.name}/props.py unchanged"))
        else:
            output_path.write_text(new_content, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[✔] {component_dir.name}/props.py updated"))

