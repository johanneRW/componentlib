import yaml
import json
from pathlib import Path

def component_import_hint_html(key):
    class_name = "".join([part.capitalize() for part in key.split("_")])
    base_path = Path(__file__).resolve().parent.parent / "components" / key

    # Læs metadata.yaml
    metadata = {}
    meta_path = base_path / "metadata.yaml"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

    # Læs example.json
    example_data = {}
    example_path = base_path / "example.json"
    if example_path.exists():
        with open(example_path, "r", encoding="utf-8") as f:
            example_data = json.load(f)

    # Saml inputs
    inputs = metadata.get("inputs", {})
    python_kwargs_list = []
    template_kwargs_list = []
    example_blocks = []

    for name in inputs.keys():
        # Placeholder til init
        placeholder = "..."
        python_kwargs_list.append(f"{name}={placeholder}")
        template_kwargs_list.append(f"{name}=value")

        # Eksempeldata blok
        if name in example_data:
            value = example_data[name]
            formatted_value = json.dumps(value, indent=2, ensure_ascii=False)
            example_blocks.append(f"{name} = {formatted_value}")

    python_kwargs_str = ", ".join(python_kwargs_list)
    template_kwargs_str = " ".join(template_kwargs_list)
    example_block_str = "\n\n".join(example_blocks) if example_blocks else ""


    # Byg HTML-sektioner
    html = f"""
<h3>Django komponent (Python)</h3>
<div class="import-block">
  <div class="code-and-button">
    <pre><code id="django-init-{key}">from componentlib.components.{key}.component import {class_name}Component

# Initiering:
{class_name}Component({python_kwargs_str})</code></pre>
    <button class="copy-btn" onclick="copySpecificCode('django-init-{key}')">
      <img class="copy-icon" src="/static/icons/copy.svg" alt="Copy"> Kopier Django initiering
    </button>
  </div>
</div>

<h3>Django komponent (template)</h3>
<div class="import-block">
  <div class="code-and-button">
    <pre><code id="django-template-{key}">{{% include \"components/{key}/template.html\" with {template_kwargs_str} %}}</code></pre>
    <button class="copy-btn" onclick="copySpecificCode('django-template-{key}')">
      <img class="copy-icon" src="/static/icons/copy.svg" alt="Copy"> Kopier Django template
    </button>
  </div>
</div>

"""

    return {
        "html": html,
        "example_block": example_block_str
    }

