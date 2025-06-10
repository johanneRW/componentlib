from componentlib.components.base import BaseComponent
from .props import DropdownComponentProps

class DropdownComponent(BaseComponent):
    template_filename = "template.html"

    def __init__(self, **kwargs):
        props = DropdownComponentProps(**kwargs)
        super().__init__(**props.dict())
        self._validated = True
