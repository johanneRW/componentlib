from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.html import escape
from pathlib import Path
from componentlib.helpers.registry import load_all_components
from componentlib.helpers.preview import render_component_preview, load_and_render_components
from componentlib.helpers.filters import filter_by_tech, filter_by_tags, search_and_sort_components
from componentlib.helpers.component_utils import collect_tags_and_tech, get_code_files
from componentlib.helpers.component_import_hint_html import get_component_import_hint, get_component_example_data


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
    all_components = sorted(all_components, key=lambda c: c.get("name", "").lower())

    # Apply technology filter
    tech_filtered_components = filter_by_tech(all_components, selected_tech)

    # Apply tag filter
    tag_filtered_components = filter_by_tags(tech_filtered_components, selected_tags)

    # Apply search filter on the already filtered components
    matched_components = search_and_sort_components(tag_filtered_components, q)
    
    # Sort alphabetically by component name
    matched_components = sorted(matched_components, key=lambda c: c.get("name", "").lower())

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
        return render(request, "component_browser/includes/results_partial.html", context)
    else:
        return render(request, "component_browser/index.html", context)


def component_detail(request, key):
    base_path = Path(__file__).resolve().parent / "components" / key

    code_files = get_code_files(base_path)

    components = sorted(load_all_components(), key=lambda c: c["name"].lower())

    # Find the current component's index
    index = next((index for index, component in enumerate(components) if component["key"] == key), None)

    if index is None:
        return render(request, "404.html", status=404)

    curr_component = components[index]
    prev_component = components[index - 1] if index > 0 else None
    next_component = components[index + 1] if index < len(components) - 1 else None

    curr_component["key"] = key
    curr_component["rendered"] = render_component_preview(key)
    import_hint = get_component_import_hint(key)
    example_data = get_component_example_data(key)

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

    return render(request, "component_browser/component_detail.html", {
        "component": curr_component,
        "previous": prev_component,
        "next": next_component,
        "import_hint": import_hint,
        "example_data": example_data,
        "code_files": code_files,
        "tech_list": tech_list,
        "doc_list": doc_list,
    })


def component_code(request, key):
    filename = request.GET.get("file")
    if not filename:
        return HttpResponseNotFound("Filename is missing.")

    base_path = Path(__file__).resolve().parent / "components" / key

    if filename == "template":
        file_path = base_path / "template.html"
    elif filename == "component":
        file_path = base_path / "component.py"
    elif filename == "props":
        file_path = base_path / "props.py"
    elif filename == "readme":
        # Look for all variants of filename ("README.md", "readme.md", "README.MD")
        file_path = None
        for fname in base_path.iterdir():
            if fname.name.lower() == "readme.md":
                file_path = fname
                break
        if not file_path:
            return HttpResponseNotFound("README.md not found.")
    else:
        return HttpResponseNotFound("Unknown file type.")

    if not file_path.exists():
        return HttpResponseNotFound("The file was not found.")

    code = file_path.read_text(encoding="utf-8")
    if filename == "readme":
        return HttpResponse(code)
    else:
        safe_code = escape(code)
        html = f"<pre><code>{safe_code}</code></pre>"
        return HttpResponse(html)
