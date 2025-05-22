from pydantic import BaseModel, Field

class FormsetTableComponentProps(BaseModel):
    formset: list = Field(Ellipsis, description='')
    columns: list = Field(Ellipsis, description='')
    content: str = Field('', description='')
    is_active: bool = Field(True, description='')
