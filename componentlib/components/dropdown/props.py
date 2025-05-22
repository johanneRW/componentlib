from pydantic import BaseModel, Field

class DropdownComponentProps(BaseModel):
    label: str = Field(..., description='Required')
    options: list = Field(..., description='Required')
    target_url: str = Field(..., description='Required')
