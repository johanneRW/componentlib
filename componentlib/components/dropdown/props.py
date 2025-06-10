__all__ = ["DropdownComponentProps"]

from pydantic import BaseModel, Field
from typing import Any, Optional

class DropdownComponentProps(BaseModel):
    value_from: Optional[str] = Field(None)
    disabled_from: Optional[str] = Field(None)
