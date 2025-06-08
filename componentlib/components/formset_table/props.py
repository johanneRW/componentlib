from pydantic import BaseModel, Field

class FormsetTableComponentProps(BaseModel):
    formset: list = Field(..., description='Required')
    columns: list = Field(..., description='Required')
    content: str = Field(..., description='Required')
    is_active: bool = Field(True)
