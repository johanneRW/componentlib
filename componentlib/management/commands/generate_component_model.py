import yaml
import json
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates props.py and example.json based on metadata.yaml"

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

            metadata_path = component_dir / "metadata.yaml"
            if not metadata_path.exists():
                self.stdout.write(self.style.WARNING(f"[SKIP] {component_dir.name} (no metadata.yaml)"))
                continue

            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = yaml.safe_load(f)

            self.generate_props(component_dir, metadata)
            self.generate_example_json(component_dir, metadata)

    def generate_props(self, component_dir: Path, metadata: dict):
        class_name = metadata.get("class_name", "UnnamedComponent")
        inputs = metadata.get("inputs", {})

        lines = [
            "from pydantic import BaseModel, Field\n",
            f"class {class_name}Props(BaseModel):"
        ]

        if not inputs:
            lines.append("    pass")
        else:
            for key, info in inputs.items():
                typ = info.get("type", "string")
                required = info.get("required", False)
                default = info.get("default", None)

                py_type = {
                    "string": "str",
                    "number": "float",
                    "boolean": "bool",
                    "list": "list",
                    "dict": "dict",
                }.get(typ, "str")

                if required:
                    line = f"    {key}: {py_type} = Field(..., description='Required')"
                else:
                    line = f"    {key}: {py_type} = Field({repr(default)})"

                lines.append(line)

        output_path = component_dir / "props.py"
        new_content = "\n".join(lines) + "\n"

        if output_path.exists() and output_path.read_text(encoding="utf-8") == new_content:
            self.stdout.write(self.style.NOTICE(f"[=] {component_dir.name}/props.py unchanged"))
        else:
            output_path.write_text(new_content, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[✔] {component_dir.name}/props.py updated"))


    def generate_example_json(self, component_dir: Path, metadata: dict):
        example_path = component_dir / "example.json"
        inputs = metadata.get("inputs", {})
        example_data = {}

        for key, info in inputs.items():
            if "default" in info:
                example_data[key] = info["default"]

        # Use ensure_ascii=False to allow non-ASCII characters in the JSON output
        new_content = json.dumps(example_data, indent=2, ensure_ascii=False)

        if example_path.exists() and example_path.read_text(encoding="utf-8").strip() == new_content.strip():
            self.stdout.write(self.style.NOTICE(f"[=] {component_dir.name}/example.json unchanged"))
        else:
            example_path.write_text(new_content + "\n", encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[✔] {component_dir.name}/example.json updated"))


