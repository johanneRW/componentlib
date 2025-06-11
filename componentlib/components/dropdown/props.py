# NOTE: This file is auto-generated.
# To update it, run: `python manage.py update_props <component_name>`
# The generation is based on template.html and example.json.
# Fields can include type/default using HTML comments:
#    {{ props.name }} <!-- type: string, default: "John" -->
# Please verify that all fields are correctly merged and validated.

__all__ = ["DropdownComponentProps"]

from pydantic import BaseModel, Field
from typing import Any, List, Optional

class DropdownComponentProps(BaseModel):
    disabled_from: Optional[bool] = Field(False)
    label: Optional[str] = Field('Vessel Type')
    name: Optional[str] = Field('vessel_type')
    options: Optional[List[Any]] = Field(...)
    placeholder: Optional[str] = Field('Select a vessel type')
    target_url: Optional[str] = Field('/htmx/generic-dropdown/')
    value_from: Optional[str] = Field(None)
