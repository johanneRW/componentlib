import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from componentlib.helpers.case_utils import CaseUtils
from componentlib.helpers.template_generator import TemplateGenerator

COMPONENTS_DIR = Path(__file__).resolve().parent.parent.parent / "components"

def yes_or_no(prompt, default="y", style=None):
    default = default.lower()
    valid = {"y": True, "n": False, "": default == "y"}

    while True:
        val = input(f"{prompt} [{'Y/n' if default == 'y' else 'y/N'}]: ").strip().lower()
        if val in ("q", "quit"):
            raise SystemExit("Aborted by user.")
        if val in valid:
            return valid[val]
        print(style.ERROR("Invalid response. Enter 'y', 'n', or 'q'") if style else "Invalid response.")

class Command(BaseCommand):
    help = "Interactive creation of a new Django component"

    def handle(self, *args, **options):
        while True:
            raw_name = input("Component name (e.g., product_card): ").strip()
            if not raw_name:
                self.stdout.write(self.style.ERROR("Name is required."))
                continue
            if not CaseUtils.is_valid_component_name(raw_name):
                self.stdout.write(self.style.ERROR("Invalid name."))
                continue

            name = CaseUtils.to_snake_case(raw_name)
            path = COMPONENTS_DIR / name

            if path.exists():
                self.stdout.write(self.style.WARNING(f"'{name}' already exists."))
                if not yes_or_no("Do you want to try another name?", default="y", style=self.style):
                    return
                continue
            break

        display_name = CaseUtils.to_title_case(name)
        class_name = f"{CaseUtils.to_pascal_case(name)}Component"
        author = input(f"Author's name [{os.getenv('USER') or 'unknown'}]: ").strip() or os.getenv("USER") or "unknown"

        include_py = yes_or_no("Create component.py?", default="y", style=self.style)
        include_html = yes_or_no("Create template.html?", default="y", style=self.style)
        include_readme = yes_or_no("Create README.md?", default="y", style=self.style)

        if not include_py and not include_html:
            raise CommandError("At least one file type must be selected.")

        context = {
            "component_name": name,
            "display_name": display_name,
            "class_name": class_name,
            "author": author,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "uuid": str(uuid.uuid4())
        }

        try:
            os.makedirs(path)
            # Create __init__.py file
            init_file = path / "__init__.py"
            init_file.touch()  # This creates an empty file
            self.stdout.write(f"  - Created __init__.py")

            templates = TemplateGenerator.generate_templates(context, include_py, include_html, include_readme)
            for filename, content in templates.items():
                with open(path / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stdout.write(f"  - Created {filename}")
            self.stdout.write(self.style.SUCCESS(f"✓ Component '{name}' created in '{path}'"))
        except Exception as e:
            if path.exists():
                shutil.rmtree(path)
            raise CommandError(f"Error during creation: {e}")
