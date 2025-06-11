import json

class TemplateGenerator:
    @staticmethod
    def generate_templates(context, include_py, include_html, include_readme):
        TEMPLATE_FILES = {}

        # Python component
        if include_py:
            TEMPLATE_FILES["component.py"] = TemplateGenerator._generate_py_template(context)

        # HTML template
        if include_html:
            TEMPLATE_FILES["template.html"] = TemplateGenerator._generate_html_template()

        # Example data
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
NOTE: Consider adding {{ attributes.class|default:'' }} to this HTML element.
This will allow for more flexible styling by enabling you to dynamically add CSS classes.
Advantages:
- Flexibility: Allows frontend developers to customize styling directly from the relevant project's stylesheet, making it easier to adapt the component's appearance to different parts of the application.
- Reusability: Increases the reusability of the component, as it can be adapted to different contexts without modifying the underlying HTML structure.
- Maintainability: Simplifies the maintenance of styling, as changes can be centralized in CSS files instead of being spread across multiple templates.

If you do not need this functionality, feel free to omit it.
Example: <div class="{{ attributes.class|default:'' }}">
-->
<div>
  {{ content }}
</div>
'''

    @staticmethod
    def _generate_example_json():
        example_data = {
            "content": "Example content"
        }
        return json.dumps(example_data, indent=2)

    @staticmethod
    def _generate_metadata_yaml(context):
        return f'''name: {context["component_name"]}
display_name: {context["display_name"]}
class_name: {context["class_name"]}
description: Write a description of the component here.
tags: []
component_data:
  author: {context["author"]}
  createdAt: {context["created_at"]}
  component_uuid: {context["uuid"]}
'''

    @staticmethod
    def _generate_props_py(context):
        props_lines = [
            "# NOTE: This file is auto-generated.",
            "# To update it, run: `python manage.py update_props <component_name>`",
            "# The generation is based on templates and example.json.",
            "# Please verify that all fields are correctly merged and that required/optional fields match the specification.\n",
            "from pydantic import BaseModel, Field\n",
            f"class {context['class_name']}Props(BaseModel):",
            "    content: str = Field(\"Example content\")"
        ]
        return "\n".join(props_lines) + "\n"


    @staticmethod
    def _generate_readme(context):
        return f"# {context['display_name']}\n\nDescription of the component, style guides, or other relevant information."
