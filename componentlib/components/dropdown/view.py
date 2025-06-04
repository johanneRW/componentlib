import json
from pathlib import Path
from django.shortcuts import render

def dropdown_htmx_view(request):
    base_path = Path(__file__).resolve().parent
    example_path = base_path / "example.json"

    context = {}

    if example_path.exists():
        with open(example_path, "r", encoding="utf-8") as f:
            context = json.load(f)

    return render(request, "components/dropdown/template.html", context)
