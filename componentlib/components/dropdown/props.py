__all__ = ["DropdownComponentProps"]

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class DropdownComponentProps(BaseModel):
    name: str = Field("dropdown")
    label: str = Field("Choose option")
    options: List[Tuple[str, str]] = Field([])
    target_url: str = Field("/htmx/dropdown/dropdown_result_view/")
    placeholder: Optional[str] = Field(None)
    value: Optional[str] = Field(None)
    disabled: bool = Field(False)

