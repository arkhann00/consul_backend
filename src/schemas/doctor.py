from datetime import datetime

from pydantic import BaseModel, Field


class DoctorBase(BaseModel):
    avatar_url: str | None = Field(None, max_length=512)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    patronymic: str | None = Field(None, max_length=100)
    position: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    avatar_url: str | None = Field(None, max_length=512)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    patronymic: str | None = Field(None, max_length=100)
    position: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
