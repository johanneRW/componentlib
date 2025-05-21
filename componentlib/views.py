from django.shortcuts import render, redirect
from .helpers.registry import load_all_components_metadata
from .helpers.preview import render_component_preview
from rapidfuzz import fuzz

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

    components = sorted(load_all_components_metadata(), key=lambda c: c["name"].lower())
    index = next((i for i, c in enumerate(components) if c["key"] == key), None)

    if index is None:
        return render(request, "404.html", status=404)

    component = components[index]
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
        "files": files,
    })


