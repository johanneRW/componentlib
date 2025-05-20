from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Viser en hjælpetekst for componentlib"

    def handle(self, *args, **options):
        self.stdout.write("""
Django ComponentLib – Hjælp

🔹 Opret en ny komponent:
    python manage.py create_component

🔹 Struktur oprettes i:
    componentlib/components/<navn>/
    ├── component.py       → Python-logik
    ├── template.html      → HTML-fragment
    ├── metadata.yaml      → Info, inputs, osv.
    ├── example.json       → Eksempel-data
    ├── example.html       → Visuelt eksempel
    └── README.md          → Valgfri dokumentation

🔹 Brug i Django:
    from componentlib import component
    html = component("button", text="Gem")

🔹 Brug i HTMX:
    <div hx-get="/components/button?text=Gem" hx-trigger="load"></div>

🔹 Se oversigt over alle komponenter:
    from componentlib import list_components
    list_components()
""")
