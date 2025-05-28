from django.shortcuts import render, redirect

from componentlib.helpers.component_import_hint_html import component_import_hint_html


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

    # Render previews
    for c in all_components:
        c["rendered"] = render_component_preview(c["key"])

    # Start med hele listen
    tag_filtered_components = all_components

    # Filtrér på tags (hvis valgt)
    if selected_tags:
        tag_filtered_components = [
            c for c in all_components
            if all(
                tag in [t.lower() for t in c.get("tags", []) if isinstance(t, str)]
                for tag in selected_tags
            )
        ]

    # Sæt tag-match flag (til visning)
    for comp in tag_filtered_components:
        tags = [t.lower() for t in comp.get("tags", []) if isinstance(t, str)]
        comp["tag_match"] = any(tag in tags for tag in selected_tags)

    # Sorter alfabetisk
    tag_filtered_components.sort(key=lambda c: c["name"].lower())

    # Søgning (hvis q angivet)
    if q:
        matched_components = []
        for c in tag_filtered_components:
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
        matched_components = tag_filtered_components

    # Saml alle tags (fra hele dataset)
    tag_set = set()
    for c in all_components:
        tag_set.update(t.lower() for t in c.get("tags", []) if isinstance(t, str))

    context = {
        "components": all_components,
        "matches": matched_components,
        "q": q,
        "selected_tags": selected_tags,
        "all_tags": sorted(tag_set),
        "only_fuzzy": q and all(m.get("match_type") == "fuzzy" for m in matched_components),
    }

    if request.headers.get("Hx-Request") == "true":
        # HTMX-anmodning → returnér kun partial-template
        return render(request, "patternlib_browser/results_partial.html", context)
    else:
        # Almindelig sideindlæsning → returnér hele layoutet
        return render(request, "patternlib_browser/index.html", context)


    
    
def component_detail(request, key):
    from .helpers.preview import render_component_preview
    from .helpers.registry import load_all_components_metadata
    from pathlib import Path

    base_path = Path(__file__).resolve().parent / "components" / key

    # Først tjek de almindelige kodefiler (template, component, props)
    code_files = []
    for f in ["template", "component", "props"]:
        ext = ".html" if f == "template" else ".py"
        file_path = base_path / f"{f}.{ext.lstrip('.')}"
        if file_path.exists():
            code_files.append(f)

    # Derefter tjek for readme (uanset case)
    for fname in base_path.iterdir():
        if fname.name.lower() == "readme.md":
            code_files.append("readme")
            break


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


    # Læs relevante kodefiler (bruges måske andetsteds)
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
        # Find README uanset case
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
    # Send RAW markdown tekst, ikke wrapped i <pre><code>
        return HttpResponse(code)
    else:
        safe_code = escape(code)
        html = f"<pre><code>{safe_code}</code></pre>"
        return HttpResponse(html)
