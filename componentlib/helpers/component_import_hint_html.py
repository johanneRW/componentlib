import json
import yaml
from textwrap import dedent
from pathlib import Path
from django.template.loader import render_to_string


def load_component_metadata(key) -> dict:
    base_path = Path(__file__).resolve().parent.parent / "components" / key
    metadata_path = base_path / "metadata.yaml"
    with open(metadata_path) as metadata:
        return yaml.load(metadata, yaml.Loader)


def get_import_hint_type(key) -> str:
    metadata = load_component_metadata(key)
    return metadata.get("import_hint_type", "")


def detect_static_include_mode(key) -> bool:
    base_path = Path(__file__).resolve().parent.parent / "components" / key
    props_path = base_path / "props.py"
    component_path = base_path / "component.py"

    if component_path.exists():
        return False

    if props_path.exists():
        content = props_path.read_text(encoding="utf-8")
        if "pass" in content and "class" in content:
            return True

    return False


def detect_unused_props_in_template(key) -> bool:
    base_path = Path(__file__).resolve().parent.parent / "components" / key
    template_path = base_path / "template.html"
    example_path = base_path / "example.json"

    if not template_path.exists() or not example_path.exists():
        return False

    try:
        example_data = json.loads(example_path.read_text(encoding="utf-8"))
        template_content = template_path.read_text(encoding="utf-8")

        for key in example_data.keys():
            if f"{{{{ {key}" in template_content:
                return False

        return True
    except Exception as e:
        #print(f"[WARN] Failed to analyze template for {key}: {e}")
        return False


def load_example_data(key):
    base_path = Path(__file__).resolve().parent.parent / "components" / key
    example_path = base_path / "example.json"
    if example_path.exists():
        try:
            content = example_path.read_text(encoding="utf-8").strip()
            if content:
                return json.loads(content)
        except json.JSONDecodeError as e:
            #print(f"[WARN] Invalid JSON in '{example_path}': {e}")
            pass
    return {}


def create_html_block(code_id, code_content, button_label):
    return render_to_string(
        "component_browser/import_hints/import_block.html",
        context={
            "code_id": code_id,
            "code_content": code_content,
            "button_label": button_label,
        }
    )


def get_component_import_hint(key):
    import_hint_type = get_import_hint_type(key)

    if import_hint_type == "template_only":
        html = get_hint_template_only(key)
    elif import_hint_type == "template_with_vars":
        html = get_hint_template_with_vars(key)
    elif import_hint_type == "inline":
        html = get_hint_inline(key)
    else:
        html = get_hint_fallback(key)

    return html


def get_component_example_data(key) -> str:
    example_data = load_example_data(key)
    example_blocks = [
        f"{name} = {json.dumps(value, indent=2, ensure_ascii=False) if value is not None else 'None'}"
        for name, value in example_data.items()
    ]
    example_block_str = "\n\n".join(example_blocks) if example_blocks else ""
    return example_block_str


def get_class_name(key) -> str:
    class_name = "".join([part.capitalize() for part in key.split("_")])
    return class_name


def get_hint_template_only(key) -> str:
    html_content = create_html_block(
        f"django-template-{key}",
        f"{{% include \"components/{key}/template.html\" %}}",
        "Copy Include Snippet"
    )
    html = f"<h3>Django Template Only</h3>{html_content}"
    return html


def get_hint_template_with_vars(key) -> str:
    example_data = load_example_data(key)
    template_kwargs_list = [f"{name}=value" for name in example_data]
    template_kwargs_str = " ".join(template_kwargs_list)
    django_template_html = create_html_block(
        f"django-template-{key}",
        f"{{% include \"components/{key}/template.html\" with {template_kwargs_str} %}}",
        "Copy Django Template"
    )
    html = f"<h3>Django Component (Template)</h3>{django_template_html}"
    return html


def get_hint_inline(key) -> str:
    class_name = get_class_name(key)
    python_expression = f'{class_name}Component(form=self.form).render()'
    django_init_html = create_html_block(
        f"django-init-{key}",
        f"from componentlib.components.{key}.component import {class_name}Component\n\n# Initialization:\n{python_expression}",
        "Copy Django Initialization"
    )
    django_template_html = create_html_block(
        f"django-template-{key}",
        f"{{{{ {key}|safe }}}}",
        "Copy Django Template"
    )
    html = dedent(
        f"""
        <h3>Django Component (Python)</h3>
        {django_init_html}
        <h3>Django Component (Template)</h3>
        {django_template_html}
        """
    )
    return html


def get_hint_fallback(key) -> str:
    class_name = get_class_name(key)
    example_data = load_example_data(key)
    python_kwargs_list = [f"{name}=..." for name in example_data]
    template_kwargs_list = [f"{name}=value" for name in example_data]
    python_kwargs_str = ", ".join(python_kwargs_list)
    template_kwargs_str = " ".join(template_kwargs_list)
    django_init_html = create_html_block(
        f"django-init-{key}",
        f"from componentlib.components.{key}.component import {class_name}Component\n\n# Initialization:\n{class_name}Component({python_kwargs_str})",
        "Copy Django Initialization"
    )
    django_template_html = create_html_block(
        f"django-template-{key}",
        f"{{% include \"components/{key}/template.html\" with {template_kwargs_str} %}}",
        "Copy Django Template"
    )
    html = dedent(
        f"""
        <h3>Django Component (Python)</h3>
        {django_init_html}
        <h3>Django Component (Template)</h3>
        {django_template_html}
        """
    )
    return html