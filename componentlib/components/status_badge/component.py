from ..base import BaseComponent
from .props import StatusBadgeComponentProps

class StatusBadgeComponent(BaseComponent):
    template_filename = "template.html"

    def __init__(self, **kwargs):
        props = StatusBadgeComponentProps(**kwargs)
        super().__init__(**props.dict())
    
    def get_context_data(self) -> dict:
        context = super().get_context_data()
        mapping = {
            "DRAFT": "badge-draft",
            "NEW": "badge-waiting",
            "APPROVED": "badge-approved",
            "REJECTED": "badge-rejected",
        }
        form = self.context["form"]
        return {"form": form, "bg": mapping[form.status]}