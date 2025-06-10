__all__ = ["StatusBadgeComponentProps"]

from typing import Any, Optional
from pydantic import BaseModel, Field

class StatusBadgeComponentProps(BaseModel):
    form: Any = Field('Django model which has a status field')
    bg: Optional[str] = Field(None)
