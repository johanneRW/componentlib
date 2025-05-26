
from pathlib import Path


def detect_component_capabilities(template_path: Path) -> dict:
    if not template_path.exists():
        return {
            "has_simple_html": False,
            "has_htmx": False,
        }

    content = template_path.read_text(encoding="utf-8").lower()
    has_htmx = any(tag in content for tag in [
        "hx-get", "hx-post", "hx-target", "hx-swap", "hx-trigger"
    ])

    return {
        "has_simple_html": not has_htmx,
        "has_htmx": has_htmx,
    }

