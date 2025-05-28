from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from pathlib import Path
from django.utils.html import escape
from .helpers.registry import load_all_components_metadata
from .helpers.preview import render_component_preview
from rapidfuzz import fuzz
from componentlib.helpers.component_import_hint_html import component_import_hint_html

def redirect_to_components(request):
    return redirect("component_browser")

def load_and_render_components():
    all_components = load_all_components_metadata()
    for c in all_components:
        c["rendered"] = render_component_preview(c["key"])
    return all_components

def filter_by_tech(components, selected_tech):
    if not selected_tech:
        return components

    def component_matches_tech(comp):
        matches = []
        if "django" in selected_tech:
            matches.append(comp["exists"].get("component_py"))
        if "html" in selected_tech:
            matches.append(comp["capabilities"].get("has_simple_html"))
        if "htmx" in selected_tech:
            matches.append(comp["capabilities"].get("has_htmx"))
        return all(matches)

    return [c for c in components if component_matches_tech(c)]

def filter_by_tags(components, selected_tags):
    if not selected_tags:
        return components

    filtered_components = []
    for c in components:
        tags = [t.lower() for t in c.get("tags", []) if isinstance(t, str)]
        if all(tag in tags for tag in selected_tags):
            filtered_components.append(c)

    return filtered_components

def search_and_sort_components(components, q):
    if not q:
        return components

    matched_components = []
    for c in components:
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
    return matched_components

def collect_tags_and_tech(components):
    tag_set = set()
    tech_set = set()

    for c in components:
        tag_set.update(t.lower() for t in c.get("tags", []) if isinstance(t, str))
        if c.get("exists", {}).get("component_py"):
            tech_set.add("django")
        if c.get("capabilities", {}).get("has_simple_html"):
            tech_set.add("html")
        if c.get("capabilities", {}).get("has_htmx"):
            tech_set.add("htmx")

    return sorted(tag_set), sorted(tech_set)

def get_code_files(base_path):
    code_files = []
    for f, ext in [("template", ".html"), ("component", ".py"), ("props", ".py")]:
        file_path = base_path / f"{f}{ext}"
        if file_path.exists():
            code_files.append(f)

    for fname in base_path.iterdir():
        if fname.name.lower() == "readme.md":
            code_files.append("readme")
            break

    return code_files

def read_files(base_path, file_names):
    files = {}
    for fname in file_names:
        path = base_path / fname
        if path.exists():
            files[fname] = path.read_text(encoding="utf-8")
    return files

def component_browser(request):
    q = request.GET.get("q", "").strip().lower()
    raw_tags = request.GET.get("tags", "")
    selected_tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
    raw_tech = request.GET.get("tech", "")
    selected_tech = [t.strip().lower() for t in raw_tech.split(",") if t.strip()]

    all_components = load_and_render_components()
    tech_filtered_components = filter_by_tech(all_components, selected_tech)
    tag_filtered_components = filter_by_tags(tech_filtered_components, selected_tags)

    for comp in tag_filtered_components:
        tags = [t.lower() for t in comp.get("tags", []) if isinstance(t, str)]
        comp["tag_match"] = any(tag in tags for tag in selected_tags)

    tag_filtered_components.sort(key=lambda c: c["name"].lower())
    matched_components = search_and_sort_components(tag_filtered_components, q)

    all_tags, all_tech = collect_tags_and_tech(all_components)

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
