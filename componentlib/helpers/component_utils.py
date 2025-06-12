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
