import os
import re
import uuid
import shutil
import json
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

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

def to_pascal_case(snake_str): return ''.join(word.capitalize() for word in snake_str.split('_'))
def to_title_case(snake_str): return ' '.join(word.capitalize() for word in snake_str.split('_'))
def to_snake_case(name): return re.sub(r'(?<!^)(?=[A-Z])', '_', name.replace("-", "_")).lower()
def is_valid_component_name(name): return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name)

def generate_templates(context, include_py, include_html, include_htmx, include_readme):
    TEMPLATE_FILES = {}

    # Python-komponent
    if include_py:
        TEMPLATE_FILES["component.py"] = f'''from componentlib.components.base import BaseComponent
from .props import {context["class_name"]}Props

class {context["class_name"]}(BaseComponent):
    template_filename = "template.html"

    def __init__(self, **kwargs):
        props = {context["class_name"]}Props(**kwargs)
        super().__init__(**props.dict())
        self._validated = True
'''

    # HTML-template
    if include_html:
        TEMPLATE_FILES["template.html"] = '''<div>
  {{ content }}
</div>
'''

    # HTMX view
    if include_htmx:
        TEMPLATE_FILES["view.py"] = f'''from django.shortcuts import render
from .component import {context["class_name"]}
import json
from pathlib import Path

def {context["component_name"]}_htmx_view(request):
    # Prøv at bruge example.json
    base_path = Path(__file__).resolve().parent
    example_path = base_path / "example.json"
    kwargs = {{}}
    if example_path.exists():
        with open(example_path, "r") as f:
            kwargs = json.load(f)

    component = {context["class_name"]}(**kwargs)
    return render(request, "components/{context["component_name"]}/template.html", component.get_context_data())
'''


    # Eksempeldata
    example_data = {
        "content": "Eksempelindhold"
    }
    if include_htmx:
        example_data["target_url"] = f"/htmx/{context['component_name']}/component_result_view/"

    TEMPLATE_FILES["example.json"] = json.dumps(example_data, indent=2)

    # metadata.yaml
    metadata_inputs = {
        "  content:\n    type: string\n    required: true\n    default: \"Eksempelindhold\""
    }
    if include_htmx:
        metadata_inputs.add(f"  target_url:\n    type: string\n    required: false\n    default: \"/htmx/{context['component_name']}/component_result_view/\"")

    metadata_inputs_block = "\n".join(sorted(metadata_inputs))

    TEMPLATE_FILES["metadata.yaml"] = f'''name: {context["component_name"]}
display_name: {context["display_name"]}
class_name: {context["class_name"]}
description: Skriv en beskrivelse af komponenten her.
tags: [{'htmx' if include_htmx else ''}]
inputs:
{metadata_inputs_block}
returns: html
component_data:
  author: {context["author"]}
  createdAt: {context["created_at"]}
  component_uuid: {context["uuid"]}
'''

    # props.py
    props_lines = [
        "from pydantic import BaseModel, Field\n",
        f"class {context['class_name']}Props(BaseModel):",
        "    content: str = Field(\"Eksempelindhold\")"
    ]
    if include_htmx:
        props_lines.append(f"    target_url: str = Field(\"/htmx/{context['component_name']}/component_result_view/\")")

    TEMPLATE_FILES["props.py"] = "\n".join(props_lines) + "\n"

    # README
    if include_readme:
        TEMPLATE_FILES["README.md"] = f"# {context['display_name']}\n\nBeskrivelse af komponenten."

    return TEMPLATE_FILES


class Command(BaseCommand):
    help = "Interaktiv oprettelse af ny Django/HTMX-komponent"

    def handle(self, *args, **options):
        while True:
            raw_name = input("Navn på komponent (fx product_card): ").strip()
            if not raw_name:
                self.stdout.write(self.style.ERROR("Navn krævet."))
                continue
            if not is_valid_component_name(raw_name):
                self.stdout.write(self.style.ERROR("Ugyldigt navn."))
                continue

            name = to_snake_case(raw_name)
            path = COMPONENTS_DIR / name

            if path.exists():
                self.stdout.write(self.style.WARNING(f"'{name}' findes allerede."))
                if not yes_or_no("Vil du prøve et andet navn?", default="y", style=self.style):
                    return
                continue
            break

        display_name = to_title_case(name)
        class_name = f"{to_pascal_case(name)}Component"
        author = input(f"Forfatterens navn [{os.getenv('USER') or 'ukendt'}]: ").strip() or os.getenv("USER") or "ukendt"

        include_py = yes_or_no("Opret component.py?", default="y", style=self.style)
        include_html = yes_or_no("Opret template.html?", default="y", style=self.style)
        include_htmx = yes_or_no("Tilføj HTMX support/view?", default="n", style=self.style)
        include_readme = yes_or_no("Opret README.md og eksempel?", default="y", style=self.style)

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
            templates = generate_templates(context, include_py, include_html, include_htmx, include_readme)
            for filename, content in templates.items():
                with open(path / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.stdout.write(f"  - Oprettet {filename}")
            self.stdout.write(self.style.SUCCESS(f"✓ Komponent '{name}' oprettet i '{path}'"))
        except Exception as e:
            if path.exists():
                shutil.rmtree(path)
            raise CommandError(f"Fejl under oprettelse: {e}")
