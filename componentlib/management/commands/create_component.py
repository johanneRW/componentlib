import os
from pathlib import Path
import shutil
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import uuid
import re
from componentlib.helpers.codegen import generate_model_class

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

def to_pascal_case(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def to_title_case(snake_str):
    return ' '.join(word.capitalize() for word in snake_str.split('_'))


def to_snake_case(name):
    name = name.replace("-", "_")  # dash til underscore
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return snake

def is_valid_component_name(name):
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None

class Command(BaseCommand):
    help = "Interaktiv oprettelse af ny komponent"
    
    def handle(self, *args, **options):
    
        # Navn – bliv ved til brugeren indtaster et gyldigt
        while True:
            raw_input_name = input("Navn på komponent (fx product_card): ").strip()
            if not raw_input_name:
                self.stdout.write(self.style.ERROR("Navn er påkrævet."))
                continue

            if not is_valid_component_name(raw_input_name):
                self.stdout.write(self.style.ERROR("Navnet må kun indeholde bogstaver, tal og underscore – og må ikke starte med et tal."))
                continue

            name = to_snake_case(raw_input_name)
            component_path = COMPONENTS_DIR / name

            if component_path.exists():
                self.stdout.write(self.style.WARNING(f"Komponenten '{name}' findes allerede."))
                try_again = yes_or_no("Vil du prøve et andet navn?", default="y", style=self.style)
                if not try_again:
                    self.stdout.write("Oprettelse afbrudt af bruger.")
                    return
                continue

            break

        #vis hvordan navnet blev fortolket
        self.stdout.write((f"Komponentnavn sat til: {name}"))

        component_name = name  # snake_case som skrevet af brugeren
        display_name = to_title_case(name)
        class_name = f"{to_pascal_case(name)}Component"


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
    "component_name": component_name,
    "display_name": display_name,
    "class_name": class_name,
    "author": author,
    "created_at": datetime.now().strftime("%Y-%m-%d"),
}

        TEMPLATE_FILES = {}

        if include_py:
            TEMPLATE_FILES["component.py"] = '''from componentlib.components.base import BaseComponent
from .types import {class_name}Props

class {class_name}(BaseComponent):
    template_filename = "template.html"

    def __init__(self, **kwargs):
        props = {class_name}Props(**kwargs)
        super().__init__(**props.dict())

    def get_context_data(self):
        return self.context
'''



        if include_html:
            TEMPLATE_FILES["template.html"] = '''{% load custom_filters %}
            <div>
{{ content }}
</div>
'''

        TEMPLATE_FILES["metadata.yaml"] = '''name: {component_name}
display_name: {display_name}
class_name: {class_name}
description: Skriv en beskrivelse af komponenten her.
tags: []
inputs:
  content:
    type: string
    required: true
    default: ""
  is_active:
    type: boolean
    required: false
    default: true
returns: html
component_data:
  author: {author}
  createdAt: {created_at}
  component_uuid: {uuid}
'''
#TODO: tilføj json til templates, find ud af om der er brug for exsample.html

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
    
        generate_model_class(component_name)



