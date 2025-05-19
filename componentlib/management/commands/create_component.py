import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import uuid

# Peg på components-mappen
COMPONENTS_DIR = Path(__file__).resolve().parent.parent.parent / "components"

# Skabelon-filer og deres indhold
TEMPLATE_FILES = {
    "component.py": '''from django.template.loader import render_to_string

class {class_name}:
    def __init__(self, **kwargs):
        self.context = kwargs

    def render(self):
        return render_to_string("components/{component_name}/template.html", self.context)
''',

    "template.html": '''<div>
  {{ content }}
</div>
''',

"metadata.yaml": '''
name: {component_name}
description: Skriv en beskrivelse her.
tags: []
inputs:
  content:
    type: string
    required: false
returns: html
component_data:
  author: {author}
  created_at: {created_at}
  component_uuid: {uuid}

''',

    "README.md": "# {component_name}\n\nSkriv en beskrivelse af denne komponent.",

   "example.json": '''{{
  "content": "Eksempeltekst"
}}''',

    "example.html": '''<!-- Visuelt eksempel på hvordan komponenten bruges. -->''',
}

class Command(BaseCommand):
    help = "Opretter en ny komponentmappe med standardfiler"

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Navn på komponenten (f.eks. 'button')")
        parser.add_argument("--author", type=str, help="Forfatternavn (valgfrit)")
        parser.add_argument("--no-readme", action="store_true", help="Udelad README.md")

    def handle(self, *args, **options):
        name = options["name"].strip().lower()
        component_path = COMPONENTS_DIR / name

        if component_path.exists():
            raise CommandError(f"Komponenten '{name}' findes allerede.")

        self.stdout.write(f"Opretter komponent: {name}")

        author = options.get("author") or os.getenv("USER") or os.getenv("USERNAME") or "ukendt"

        context = {
            "uuid": str(uuid.uuid4()),
            "component_name": name,
            "class_name": f"{name.capitalize()}Component",
            "author": author,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
        }

        # ➕ Filindhold forberedes
        try:
            file_contents = {}
            for filename, content in TEMPLATE_FILES.items():
                if filename == "README.md" and options.get("no_readme"):
                    continue  # Skipper README hvis valgt
                file_contents[filename] = content.format(**context)
        except KeyError as e:
            raise CommandError(f"Fejl i skabelon: mangler nøgle {e}")

        # ✅ Opret og skriv filer
        try:
            os.makedirs(component_path)
            for filename, content in file_contents.items():
                filepath = component_path / filename
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stdout.write(f"  - Oprettet {filename}")

            self.stdout.write(self.style.SUCCESS(f"Komponent '{name}' oprettet korrekt i 'components/{name}/'"))

        except Exception as e:
            if component_path.exists():
                import shutil
                shutil.rmtree(component_path)
            raise CommandError(f"Fejl under oprettelse af komponenten: {e}")


