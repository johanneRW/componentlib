__all__ = ["DropdownComponentProps"]

from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class DropdownComponentProps(BaseModel):
    name: str = Field(..., description="Name of the dropdown field")
    label: str = Field(..., description="Label for the dropdown field")
    options: List[Tuple[str, str]] = Field(default_factory=list, description="List of options for the dropdown")
    target_url: str = Field(..., description="URL to fetch dropdown options from")
    placeholder: Optional[str] = Field(None, description="Placeholder text for the dropdown")
    value_from: Optional[str] = Field(None, description="Initial value for the dropdown")
    disabled_from: bool = Field(False, description="Whether the dropdown is disabled")