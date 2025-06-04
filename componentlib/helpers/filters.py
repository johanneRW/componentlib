from rapidfuzz import fuzz

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

