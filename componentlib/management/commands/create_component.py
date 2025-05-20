import os
from pathlib import Path
import shutil
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import uuid

COMPONENTS_DIR = Path(__file__).resolve().parent.parent.parent / "components"

def yes_or_no(prompt, default="y", style=None):
    default = default.lower()
    valid = {"y": True, "n": False, "": default == "y"}

    while True:
        val = input(f"{prompt} [{'Y/n' if default == 'y' else 'y/N'}]: ").strip().lower()

        if val in ("q", "quit"):
            msg = "Afbrudt af bruger."
            print(msg)
            raise SystemExit

        if val in valid:
            return valid[val]

        msg = "Ugyldigt svar. Skriv 'y' for ja, 'n' for nej eller 'q' for at afbryde."
        print(style.ERROR(msg) if style else msg)




class Command(BaseCommand):
    help = "Interaktiv oprettelse af ny komponent"
    
    def handle(self, *args, **options):
    
        # Navn – bliv ved til brugeren indtaster et gyldigt
        while True:
            name = input("Navn på komponent (fx button): ").strip().lower()
            if not name:
                self.stdout.write(self.style.ERROR("Navn er påkrævet."))
                continue

            component_path = COMPONENTS_DIR / name
            if component_path.exists():
                self.stdout.write(self.style.WARNING(f"Komponenten '{name}' findes allerede."))
                try_again = yes_or_no("Vil du prøve et andet navn?", default="y", style=self.style)
                if not try_again:
                    print("Oprettelse afbrudt af bruger.")
                    return
                continue  # prøv igen med nyt navn
            break  # navn er OK – gå videre til komponent-oprettelse


        include_py = yes_or_no("Opret component.py?", default="y", style=self.style)
        include_html = yes_or_no("Opret template.html?", default="y",  style=self.style)


        if not include_py and not include_html:
            raise CommandError("Du skal vælge mindst én filtype (Python eller HTML). Komponenten blev ikke oprettet.")
        
        include_readme = yes_or_no("Opret README.md og eksempelfiler?", default="y", style=self.style)

        author = input(f"Forfatterens navn [default: {os.getenv('USER') or 'ukendt'}]: ").strip()
        if not author:
            author = os.getenv("USER") or "ukendt"

        context = {
            "uuid": str(uuid.uuid4()),
            "component_name": name,
            "class_name": f"{name.capitalize()}Component",
            "author": author,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
        }

        TEMPLATE_FILES = {}

        if include_py:
            TEMPLATE_FILES["component.py"] = '''from django.template.loader import render_to_string

class {class_name}:
def __init__(self, **kwargs):
    self.context = kwargs

def render(self):
    return render_to_string("components/{component_name}/template.html", self.context)
'''

        if include_html:
            TEMPLATE_FILES["template.html"] = '''<div>
{{ content }}
</div>
'''

        TEMPLATE_FILES["metadata.yaml"] = '''name: {component_name}
description: Skriv en af beskrivelse komponenten her.
tags: []
inputs:
content:
type: 
required: 
returns: 
component_data:
author: {author}
created_at: {created_at}
component_uuid: {uuid}
'''

        if include_readme:
            TEMPLATE_FILES["README.md"] = "# {component_name}\n\nSkriv en beskrivelse af denne komponent."
            TEMPLATE_FILES["example.html"] = '''{{"content": "Eksempeltekst" }}'''

        # Forbered filindhold
        try:
            file_contents = {}
            for filename, content in TEMPLATE_FILES.items():
                file_contents[filename] = content.format(**context)
        except KeyError as e:
            raise CommandError(f"Fejl i skabelon: mangler nøgle {e}")

        # Skriv filerne
        try:
            os.makedirs(component_path)
            for filename, content in file_contents.items():
                with open(component_path / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stdout.write(f"  - Oprettet {filename}")
            self.stdout.write(self.style.SUCCESS(f"Komponent '{name}' oprettet i '{component_path}'"))
        except Exception as e:
            if component_path.exists():
                shutil.rmtree(component_path)
            raise CommandError(f"Fejl under oprettelse: {e}")



