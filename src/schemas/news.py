from datetime import datetime

from pydantic import BaseModel, Field


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    image: str | None = Field(None, max_length=512)


class NewsCreate(NewsBase):
    pass


class NewsUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    image: str | None = Field(None, max_length=512)


class NewsResponse(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
