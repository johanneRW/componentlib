__all__ = ["LanguageDropdownComponentProps"]

from pydantic import BaseModel, Field

class LanguageDropdownComponentProps(BaseModel):
    content: str = Field('Example content')
