import json

class TemplateGenerator:
    @staticmethod
    def generate_templates(context, include_py, include_html, include_readme):
        TEMPLATE_FILES = {}

        # Python-komponent
        if include_py:
            TEMPLATE_FILES["component.py"] = TemplateGenerator._generate_py_template(context)

        # HTML-template
        if include_html:
            TEMPLATE_FILES["template.html"] = TemplateGenerator._generate_html_template()

        # Eksempeldata
        TEMPLATE_FILES["example.json"] = TemplateGenerator._generate_example_json()

        # metadata.yaml
        TEMPLATE_FILES["metadata.yaml"] = TemplateGenerator._generate_metadata_yaml(context)

        # props.py
        TEMPLATE_FILES["props.py"] = TemplateGenerator._generate_props_py(context)

        # README
        if include_readme:
            TEMPLATE_FILES["README.md"] = TemplateGenerator._generate_readme(context)

        return TEMPLATE_FILES

    @staticmethod
    def _generate_py_template(context):
        return f'''from componentlib.components.base import BaseComponent
from .props import {context["class_name"]}Props

class {context["class_name"]}(BaseComponent):
    template_filename = "template.html"

    def __init__(self, **kwargs):
        props = {context["class_name"]}Props(**kwargs)
        super().__init__(**props.dict())
'''

    @staticmethod
    def _generate_html_template():
        return '''<!--
TODO: Overvej at tilføje {{ attributes.class if attributes.class else '' }} til dette HTML-element.
Dette vil tillade mere fleksibel styling ved at give dig mulighed for at tilføje CSS-klasser dynamisk.
Fordele:
- Fleksibilitet: Giver frontend-udviklere mulighed for at tilpasse styling direkte fra det relevante projekts stylesheet, hvilket gør det nemmere at tilpasse komponentens udseende til forskellige dele af applikationen.
- Genanvendelighed: Øger komponentens genanvendelighed, da den kan tilpasses til forskellige kontekster uden at skulle ændre den underliggende HTML-struktur.
- Vedligeholdelse: Foreenkler vedligeholdelsen af styling, da ændringer kan centraliseres i CSS-filer i stedet for at skulle spredes ud over flere templates.

Hvis du ikke har brug for denne funktionalitet, kan du frit vælge at udelade det.
Eksempel: <div class="{{ attributes.class if attributes.class else '' }}">
-->
<div>
  {{ content }}
</div>
'''

    @staticmethod
    def _generate_example_json():
        example_data = {
            "content": "Eksempelindhold"
        }
        return json.dumps(example_data, indent=2)

    @staticmethod
    def _generate_metadata_yaml(context):
        metadata_inputs_block = "  content:\n    type: string\n    required: true\n    default: \"Eksempelindhold\""
        return f'''name: {context["component_name"]}
display_name: {context["display_name"]}
class_name: {context["class_name"]}
description: Skriv en beskrivelse af komponenten her.
tags: []
inputs:
{metadata_inputs_block}
returns: html
component_data:
  author: {context["author"]}
  createdAt: {context["created_at"]}
  component_uuid: {context["uuid"]}
'''

    @staticmethod
    def _generate_props_py(context):
        props_lines = [
            "from pydantic import BaseModel, Field\n",
            f"class {context['class_name']}Props(BaseModel):",
            "    content: str = Field(\"Eksempelindhold\")"
        ]
        return "\n".join(props_lines) + "\n"

    @staticmethod
    def _generate_readme(context):
        return f"# {context['display_name']}\n\nBeskrivelse af komponenten, stilguides eller andet relevant."
