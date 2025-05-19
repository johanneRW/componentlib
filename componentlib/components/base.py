from pathlib import Path
from django.template import engines

class BaseComponent:
    template_filename = "template.html"

    def render(self) -> str:
        path = Path(__file__).resolve().parent / self.template_filename
        template_string = path.read_text(encoding="utf-8")
        django_engine = engines["django"]
        template = django_engine.from_string(template_string)
        return template.render(self.get_context_data())

    def get_context_data(self) -> dict:
        """Skal overskrives i child-klassen med relevante data"""
        return {}
