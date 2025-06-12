# NOTE: This file is auto-generated.
# To update it, run: `python manage.py update_props <component_name>`
# The generation is based on template.html and example.json.
# Fields can include type/default using HTML comments:
#    {{ props.name }} <!-- type: string, default: "John" -->
# Please verify that all fields are correctly merged and validated.

__all__ = ["StatusBadgeComponentProps"]

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class StatusBadgeComponentProps(BaseModel):
    form: Optional[Dict[str, Any]] = Field(...)
