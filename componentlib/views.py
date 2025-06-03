from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from pathlib import Path
from django.utils.html import escape
from componentlib.helpers.registry import load_all_components_metadata
from componentlib.helpers.preview import render_component_preview
from componentlib.helpers.filters import filter_by_tech, filter_by_tags, search_and_sort_components
from componentlib.helpers.component_utils import load_and_render_components, collect_tags_and_tech, get_code_files, read_files
from componentlib.helpers.component_import_hint_html import component_import_hint_html

def redirect_to_components(request):
    return redirect("component_browser")


def component_browser(request):
    # Get query parameters from the request
    q = request.GET.get("q", "").strip().lower()
    raw_tags = request.GET.get("tags", "")
    selected_tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
    raw_tech = request.GET.get("tech", "")
    selected_tech = [t.strip().lower() for t in raw_tech.split(",") if t.strip()]

    # Load and render all components
    all_components = load_and_render_components()

    # Apply technology filter
    tech_filtered_components = filter_by_tech(all_components, selected_tech)

    # Apply tag filter
    tag_filtered_components = filter_by_tags(tech_filtered_components, selected_tags)

    # Apply search filter on the already filtered components
    matched_components = search_and_sort_components(tag_filtered_components, q)

    # Collect all tags and technologies for the UI
    all_tags, all_tech = collect_tags_and_tech(all_components)

    # Prepare context for rendering
    context = {
        "components": all_components,
        "matches": matched_components,
        "q": q,
        "selected_tags": selected_tags,
        "selected_tech": selected_tech,
        "all_tags": all_tags,
        "all_tech": all_tech,
        "only_fuzzy": q and all(m.get("match_type") == "fuzzy" for m in matched_components),
    }

    # Render the appropriate template based on the request type
    if request.headers.get("Hx-Request") == "true":
        return render(request, "patternlib_browser/results_partial.html", context)
    else:
        return render(request, "patternlib_browser/index.html", context)



def component_detail(request, key):
    base_path = Path(__file__).resolve().parent / "components" / key

    code_files = get_code_files(base_path)

    components = sorted(load_all_components_metadata(), key=lambda c: c["name"].lower())
    index = next((i for i, c in enumerate(components) if c["key"] == key), None)

    if index is None:
        return render(request, "404.html", status=404)

    component = components[index]
    component["key"] = key
    component["rendered"] = render_component_preview(key)
    hint_data = component_import_hint_html(component['key'])
    component['import_hint'] = hint_data['html']
    component['example_data_block'] = hint_data['example_block']

    file_names = ["template.html", "component.py", "metadata.yaml", "example.json", "README.md"]
    files = read_files(base_path, file_names)

    previous = components[index - 1] if index > 0 else None
    next_comp = components[index + 1] if index < len(components) - 1 else None

    tech_list = [
        {'name': 'django', 'icon': 'django.svg', 'alt': 'Django', 'label': 'Django'},
        {'name': 'html', 'icon': 'template.svg', 'alt': 'HTML', 'label': 'HTML'},
        {'name': 'htmx', 'icon': 'htmx.svg', 'alt': 'HTMX', 'label': 'HTMX'},
    ]

    doc_list = [
        {'exists_key': 'metadata_yaml', 'icon': 'metadata.svg', 'alt': 'metadata icon', 'extension': '.yaml'},
        {'exists_key': 'example_json', 'icon': 'example_json.svg', 'alt': 'example json icon', 'extension': '.json'},
        {'exists_key': 'readme_md', 'icon': 'readme.svg', 'alt': 'readme icon', 'extension': '.md'},
    ]

    return render(request, "patternlib_browser/component_detail.html", {
        "component": component,
        "previous": previous,
        "next": next_comp,
        "code_files": code_files,
        "tech_list": tech_list,
        "doc_list": doc_list,
    })

def component_code(request, key):
    filename = request.GET.get("file")
    if not filename:
        return HttpResponseNotFound("Filnavn mangler.")

    base_path = Path(__file__).resolve().parent / "components" / key

    if filename == "template":
        file_path = base_path / "template.html"
    elif filename == "component":
        file_path = base_path / "component.py"
    elif filename == "props":
        file_path = base_path / "props.py"
    elif filename == "readme":
        file_path = None
        for fname in base_path.iterdir():
            if fname.name.lower() == "readme.md":
                file_path = fname
                break
        if not file_path:
            return HttpResponseNotFound("README.md ikke fundet.")
    else:
        return HttpResponseNotFound("Ukendt filtype.")

    if not file_path.exists():
        return HttpResponseNotFound("Filen blev ikke fundet.")

    code = file_path.read_text(encoding="utf-8")
    if filename == "readme":
        return HttpResponse(code)
    else:
        safe_code = escape(code)
        html = f"<pre><code>{safe_code}</code></pre>"
        return HttpResponse(html)
