__all__ = ["DropdownComponentProps"]

from pydantic import BaseModel, Field
from typing import Any, List, Optional, Tuple

class DropdownComponentProps(BaseModel):
    name: str = Field('nationality')
    label: str = Field('Nationality')
    options: List[Tuple[str, str]] = Field([['DK', 'Danmark'], ['NO', 'Norge'], ['SE', 'Sverige']])
    target_url: str = Field('/htmx/dropdown/dropdown_result_view/')
    placeholder: Optional[Any] = Field(None)
