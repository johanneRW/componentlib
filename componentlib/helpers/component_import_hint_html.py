import yaml
import json
from pathlib import Path

def component_import_hint_html(key):
    class_name = "".join([part.capitalize() for part in key.split("_")])
    base_path = Path(__file__).resolve().parent.parent / "components" / key

    # Read metadata.yaml (still optional for future use)
    metadata = {}
    meta_path = base_path / "metadata.yaml"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

    # Read example.json
    example_data = {}
    example_path = base_path / "example.json"
    if example_path.exists():
        with open(example_path, "r", encoding="utf-8") as f:
            example_data = json.load(f)

    # Generate blocks based only on example.json keys
    python_kwargs_list = []
    template_kwargs_list = []
    example_blocks = []

    for name, value in example_data.items():
        python_kwargs_list.append(f"{name}=...")
        template_kwargs_list.append(f"{name}=value")

        if value is None:
            formatted_value = "None"
        else:
            formatted_value = json.dumps(value, indent=2, ensure_ascii=False)

        example_blocks.append(f"{name} = {formatted_value}")



    python_kwargs_str = ", ".join(python_kwargs_list)
    template_kwargs_str = " ".join(template_kwargs_list)
    example_block_str = "\n\n".join(example_blocks) if example_blocks else ""

    # Build HTML
    html = f"""
<h3>Django Component (Python)</h3>
<div class="import-block">
  <div class="code-and-button">
    <pre><code id="django-init-{key}">from componentlib.components.{key}.component import {class_name}Component

# Initialization:
{class_name}Component({python_kwargs_str})</code></pre>
    <button class="copy-btn"
            hx-get="/dummy-endpoint"
            hx-trigger="click"
            data-code-id="django-init-{key}">
        <img class="copy-icon" src="/static/icons/copy.svg" alt="Copy"> Copy Django Initialization
    </button>
  </div>
</div>

<h3>Django Component (Template)</h3>
<div class="import-block">
  <div class="code-and-button">
    <pre><code id="django-template-{key}">{{% include \"components/{key}/template.html\" with {template_kwargs_str} %}}</code></pre>

    <button class="copy-btn"
            hx-get="/dummy-endpoint"
            hx-trigger="click"
            data-code-id="django-template-{key}">
        <img class="copy-icon" src="/static/icons/copy.svg" alt="Copy"> Copy Django Template
    </button>
    
  </div>
</div>
"""

    return {
        "html": html,
        "example_block": example_block_str
    }
