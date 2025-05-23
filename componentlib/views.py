from django.shortcuts import render, redirect
from .helpers.registry import load_all_components_metadata
from .helpers.preview import render_component_preview
from rapidfuzz import fuzz
from django.http import HttpResponse, Http404, HttpResponseNotFound
from pathlib import Path
from django.utils.html import escape

def redirect_to_components(request):
    return redirect("component_browser")

def component_browser(request):
    q = request.GET.get("q", "").strip().lower()
    raw_tags = request.GET.get("tags", "")
    selected_tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]


    all_components = load_all_components_metadata()

    # Render preview
    for c in all_components:
        c["rendered"] = render_component_preview(c["key"])

    # Filtrér på tag hvis valgt
    if selected_tags:
        all_components = [
            c for c in all_components
            if all(
                tag in [t.lower() for t in c.get("tags", []) if isinstance(t, str)]
                for tag in selected_tags
            )
    ]
        
    for comp in all_components:
        tags = [t.lower() for t in comp.get("tags", []) if isinstance(t, str)]
        comp["tag_match"] = any(tag in tags for tag in selected_tags)


    # Sortér til oversigt
    all_components.sort(key=lambda c: c["name"].lower())

    # Match via navn + beskrivelse + tags (kun hvis søgeord givet)
    matched_components = []
    if q:
        for c in all_components:
            haystack = " ".join([
                c.get("name", ""),
                c.get("description", ""),
                " ".join([t for t in c.get("tags", []) if isinstance(t, str)]),
            ]).lower()

            if q in haystack:
                c["match_type"] = "substring"
                matched_components.append(c)
            else:
                score = fuzz.partial_ratio(q, haystack)
                if score > 60:
                    c["fuzzy_score"] = score
                    c["match_type"] = "fuzzy"
                    matched_components.append(c)

        matched_components.sort(key=lambda x: x.get("fuzzy_score", 0), reverse=True)
    else:
        matched_components = all_components

    # Saml alle tags
    tag_set = set()
    for c in load_all_components_metadata():  # alle, ikke filtrerede
        tag_set.update(t.lower() for t in c.get("tags", []) if isinstance(t, str))

    return render(request, "patternlib_browser/index.html", {
        "components": all_components,
        "matches": matched_components,
        "q": q,
        "selected_tags": selected_tags,
        "all_tags": sorted(tag_set),
        "only_fuzzy": q and all(m.get("match_type") == "fuzzy" for m in matched_components),
    })

    
    
def component_detail(request, key):
    from .helpers.preview import render_component_preview
    from .helpers.registry import load_all_components_metadata
    from pathlib import Path
    
    base_path = Path(__file__).resolve().parent / "components" / key
    
    code_files = []
    for f in ["template", "component", "props", "view"]:
        ext = ".html" if f == "template" else ".py"
        if (base_path / f"{f}.{ext.lstrip('.')}").exists():
            code_files.append(f)

    components = sorted(load_all_components_metadata(), key=lambda c: c["name"].lower())
    index = next((i for i, c in enumerate(components) if c["key"] == key), None)

    if index is None:
        return render(request, "404.html", status=404)

    component = components[index]
    component["key"] = key
    component["rendered"] = render_component_preview(key)
    

    # Læs relevante kodefiler
    base_path = Path(__file__).resolve().parent / "components" / key
    file_names = ["template.html", "component.py", "metadata.yaml", "example.json", "README.md"]
    files = {}
    for fname in file_names:
        path = base_path / fname
        if path.exists():
            files[fname] = path.read_text(encoding="utf-8")

    previous = components[index - 1] if index > 0 else None
    next_comp = components[index + 1] if index < len(components) - 1 else None

    return render(request, "patternlib_browser/component_detail.html", {
    "component": component,
    "previous": previous,
    "next": next_comp,
    "code_files": code_files,
})



from django.http import HttpResponse, HttpResponseNotFound
from pathlib import Path
from django.utils.html import escape

def component_code(request, key):
    filename = request.GET.get("file")
    hide = request.GET.get("hide") == "true"

    # Skjul logik – returnér tomt HTML
    if hide:
        return HttpResponse("")

    # Find filstien
    ext = ".html" if filename == "template" else ".py"
    file_path = Path(__file__).resolve().parent / "components" / key / f"{filename}{ext}"

    if not file_path.exists():
        return HttpResponseNotFound("Filen blev ikke fundet.")

    # Læs og escap koden
    code = file_path.read_text(encoding="utf-8")
    safe_code = escape(code)

    # Returnér HTML med "Skjul"-knap der laver ny GET med ?hide=true
    html = f"""
      <div>
        <button
          hx-get="{request.build_absolute_uri()}&hide=true"
          hx-target="#code-block-{filename}"
          hx-swap="innerHTML"
        >Skjul</button>
        <pre><code>{safe_code}</code></pre>
      </div>
    """
    return HttpResponse(html)


import yaml
import json
from pathlib import Path
from django.http import HttpResponse


def component_import_hint(request, key):
    class_name = "".join([part.capitalize() for part in key.split("_")])
    view_name = f"{key}_htmx_view"
    base_path = Path(__file__).resolve().parent / "components" / key

    # Læs metadata.yaml (valgfrit)
    metadata = {}
    meta_path = base_path / "metadata.yaml"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

    # Læs example.json (valgfrit)
    example_path = base_path / "example.json"
    example_data = {}
    if example_path.exists():
        with open(example_path, "r", encoding="utf-8") as f:
            example_data = json.load(f)

    # Lav kwargs til Python-eksempel
    inputs = metadata.get("inputs", {})
    kwargs_list = []
    for name, info in inputs.items():
        val = example_data.get(name, info.get("default", ""))
        val_repr = f'"{val}"' if isinstance(val, str) else str(val)
        kwargs_list.append(f"{name}={val_repr}")
    kwargs_str = ", ".join(kwargs_list)

    html = f"""
<h3>Django komponent</h3>
<div class="import-block">
  <button class="copy-btn" onclick="copyToClipboard(this)">📋</button>
  <pre><code>from componentlib.components.{key}.component import {class_name}Component

# Eksempel:
component = {class_name}Component({kwargs_str})
html = component.render()
</code></pre>
</div>

<h3>HTMX komponent</h3>
<div class="import-block">
  <button class="copy-btn" onclick="copyToClipboard(this)">📋</button>
  <pre><code>from componentlib.components.{key}.view import {view_name}

# urls.py i dit projekt:
path("htmx/{key}/", {view_name}, name="{view_name}")

# template.html i dit projekt:
&lt;div 
  hx-get="{{% url '{view_name}' %}}" 
  hx-target="#target-{key}" 
  hx-swap="innerHTML"&gt;
&lt;/div&gt;

&lt;div id="target-{key}"&gt;&lt;/div&gt;

&lt;script src="https://unpkg.com/htmx.org@1.9.10"&gt;&lt;/script&gt;
</code></pre>
</div>
"""

    return HttpResponse(html)

