import inspect
from pathlib import Path
from django.template import engines

class BaseComponent:
    template_filename = "template.html"

    def __init__(self, base_path=None, **kwargs):
        self.base_path = Path(base_path) if base_path else Path(inspect.getfile(self.__class__)).resolve().parent

        # Internal context
        self.context = kwargs.copy()

        # # Insert dynamic fields before rendering
        # self.apply_dynamic_fields()

        # Warn if props are not used
        if not getattr(self, "_validated", False):
            #print(f"[WARNING] {self.__class__.__name__} input not validated via Props model.")
            pass



    def get_context_data(self) -> dict:
        return self.context

    def render(self) -> str:
        template_path = self.base_path / self.template_filename
        template_string = template_path.read_text(encoding="utf-8")
        django_engine = engines["django"]
        template = django_engine.from_string(template_string)
        return template.render(self.get_context_data())
