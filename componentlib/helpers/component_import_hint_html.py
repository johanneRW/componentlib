import importlib
import inspect
import json
from pathlib import Path

def detect_render_mode(key) -> str:
    module_path = f"componentlib.components.{key}.component"
    class_name = "".join([part.capitalize() for part in key.split("_")]) + "Component"

    try:
        module = importlib.import_module(module_path)
        component_cls = getattr(module, class_name)

        if hasattr(component_cls, "get_context_data"):
            source = inspect.getsource(component_cls.get_context_data)
            if "return super().get_context_data()" in source:
                return "include"
            elif "return {" in source:
                return "inline"
    except Exception as e:
        print(f"[WARN] Could not analyse component '{key}': {e}")

    return "include"

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
        print(f"[WARN] Failed to analyze template for {key}: {e}")
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
            print(f"[WARN] Invalid JSON in '{example_path}': {e}")
    return {}

def create_html_block(code_id, code_content, button_label):
    return f"""
<div class="import-block">
  <div class="code-and-button">
    <pre><code id="{code_id}">{code_content}</code></pre>
    <button class="copy-btn"
            hx-get="/dummy-endpoint"
            hx-trigger="click"
            data-code-id="{code_id}">
        <img class="copy-icon" src="/static/icons/copy.svg" alt="Copy"> {button_label}
    </button>
  </div>
</div>
"""

def component_import_hint_html(key):
    class_name = "".join([part.capitalize() for part in key.split("_")])
    base_path = Path(__file__).resolve().parent.parent / "components" / key
    example_data = load_example_data(key)
    render_mode = detect_render_mode(key)

    example_blocks = [
        f"{name} = {json.dumps(value, indent=2, ensure_ascii=False) if value is not None else 'None'}"
        for name, value in example_data.items()
    ]
    example_block_str = "\n\n".join(example_blocks) if example_blocks else ""

    component_path = base_path / "component.py"
    template_path = base_path / "template.html"
    example_path = base_path / "example.json"

    if detect_static_include_mode(key) or detect_unused_props_in_template(key):
        html_content = create_html_block(
            f"django-template-{key}",
            f"{{% include \"components/{key}/template.html\" %}}",
            "Copy Include Snippet"
        )
        return {"html": f"<h3>Django Template Only</h3>{html_content}", "example_block": example_block_str}

    elif not component_path.exists() and template_path.exists() and example_path.exists():
        python_kwargs_list = [f"{name}=..." for name in example_data]
        template_kwargs_list = [f"{name}=value" for name in example_data]
        template_kwargs_str = " ".join(template_kwargs_list)

        django_template_html = create_html_block(
            f"django-template-{key}",
            f"{{% include \"components/{key}/template.html\" with {template_kwargs_str} %}}",
            "Copy Django Template"
        )
        html = f"""
<h3>Django Component (Template)</h3>
{django_template_html}
"""
        return {"html": html, "example_block": example_block_str}

    elif render_mode == "inline":
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
        html = f"""
<h3>Django Component (Python)</h3>
{django_init_html}
<h3>Django Component (Template)</h3>
{django_template_html}
"""
    else:
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
        html = f"""
<h3>Django Component (Python)</h3>
{django_init_html}
<h3>Django Component (Template)</h3>
{django_template_html}
"""

    return {"html": html, "example_block": example_block_str}
