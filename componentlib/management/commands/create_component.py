import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from case_utils import CaseUtils
from template_generator import TemplateGenerator

COMPONENTS_DIR = Path(__file__).resolve().parent.parent.parent / "components"

def yes_or_no(prompt, default="y", style=None):
    default = default.lower()
    valid = {"y": True, "n": False, "": default == "y"}

    while True:
        val = input(f"{prompt} [{'Y/n' if default == 'y' else 'y/N'}]: ").strip().lower()
        if val in ("q", "quit"):
            raise SystemExit("Afbrudt af bruger.")
        if val in valid:
            return valid[val]
        print(style.ERROR("Ugyldigt svar. Skriv 'y', 'n' eller 'q'") if style else "Ugyldigt svar.")

class Command(BaseCommand):
    help = "Interaktiv oprettelse af ny Django-komponent"

    def handle(self, *args, **options):
        while True:
            raw_name = input("Navn på komponent (fx product_card): ").strip()
            if not raw_name:
                self.stdout.write(self.style.ERROR("Navn krævet."))
                continue
            if not CaseUtils.is_valid_component_name(raw_name):
                self.stdout.write(self.style.ERROR("Ugyldigt navn."))
                continue

            name = CaseUtils.to_snake_case(raw_name)
            path = COMPONENTS_DIR / name

            if path.exists():
                self.stdout.write(self.style.WARNING(f"'{name}' findes allerede."))
                if not yes_or_no("Vil du prøve et andet navn?", default="y", style=self.style):
                    return
                continue
            break

        display_name = CaseUtils.to_title_case(name)
        class_name = f"{CaseUtils.to_pascal_case(name)}Component"
        author = input(f"Forfatterens navn [{os.getenv('USER') or 'ukendt'}]: ").strip() or os.getenv("USER") or "ukendt"

        include_py = yes_or_no("Opret component.py?", default="y", style=self.style)
        include_html = yes_or_no("Opret template.html?", default="y", style=self.style)
        include_readme = yes_or_no("Opret README.md?", default="y", style=self.style)

        if not include_py and not include_html:
            raise CommandError("Skal vælge mindst én filtype.")

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
            templates = TemplateGenerator.generate_templates(context, include_py, include_html, include_readme)
            for filename, content in templates.items():
                with open(path / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stdout.write(f"  - Oprettet {filename}")
            self.stdout.write(self.style.SUCCESS(f"✓ Komponent '{name}' oprettet i '{path}'"))
        except Exception as e:
            if path.exists():
                shutil.rmtree(path)
            raise CommandError(f"Fejl under oprettelse: {e}")
