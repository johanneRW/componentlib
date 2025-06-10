from componentlib.components.base import BaseComponent
from .props import LanguageDropdownComponentProps

class LanguageDropdownComponent(BaseComponent):
    template_filename = "template.html"

    def __init__(self, **kwargs):
        props = LanguageDropdownComponentProps(**kwargs)
        super().__init__(**props.dict())
