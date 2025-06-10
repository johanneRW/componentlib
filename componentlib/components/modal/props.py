from pydantic import BaseModel, Field

class ModalComponentProps(BaseModel):
    content: str = Field("Example content")
