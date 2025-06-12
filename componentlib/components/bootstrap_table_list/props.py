# NOTE: This file is auto-generated.
# To update it, run: `python manage.py update_props <component_name>`
# The generation is based on template.html and example.json.
# Fields can include type/default using HTML comments:
#    {{ props.name }} <!-- type: string, default: "John" -->
# Please verify that all fields are correctly merged and validated.

__all__ = ["BootstrapTableListComponentProps"]

from pydantic import BaseModel, Field
from typing import Optional

class BootstrapTableListComponentProps(BaseModel):
    content: Optional[str] = Field('Example content')
