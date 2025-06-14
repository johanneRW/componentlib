# NOTE: This file is auto-generated.
# To update it, run: `python manage.py update_props <component_name>`
# The generation is based on template.html and example.json.
# Fields can include type/default using HTML comments:
#    {{ props.name }} <!-- type: string, default: "John" -->
# Please verify that all fields are correctly merged and validated.

__all__ = ["BootstrapTableListComponentProps"]

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class BootstrapTableListComponentProps(BaseModel):
    can_edit_multiple: Optional[bool] = Field(True)
    columns: Optional[List[Any]] = Field(...)
    items: Optional[List[Any]] = Field(...)
    search_data: Optional[Dict[str, Any]] = Field(...)
    total: Optional[float] = Field(1000)
