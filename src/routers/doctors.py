from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_admin
from database import get_db
from models.doctor import Doctor
from models.user import User
from schemas.doctor import DoctorCreate, DoctorResponse, DoctorUpdate
from utils.uploads import save_upload

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorResponse])
def list_doctors(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[Doctor]:
    return db.query(Doctor).offset(skip).limit(limit).all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    position: Annotated[str, Form()],
    patronymic: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    avatar_url: Annotated[str | None, Form()] = None,
    avatar: Annotated[UploadFile | None, File()] = None,
) -> Doctor:
    if avatar is not None and avatar.filename:
        avatar_url = await save_upload(avatar, "doctors")

    doctor = Doctor(
        avatar_url=avatar_url,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        position=position,
        description=description,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.post("/json", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor_json(
    data: DoctorCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> Doctor:
    doctor = Doctor(**data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
    first_name: Annotated[str | None, Form()] = None,
    last_name: Annotated[str | None, Form()] = None,
    patronymic: Annotated[str | None, Form()] = None,
    position: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    avatar_url: Annotated[str | None, Form()] = None,
    avatar: Annotated[UploadFile | None, File()] = None,
) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if avatar is not None and avatar.filename:
        avatar_url = await save_upload(avatar, "doctors")
    if avatar_url is not None:
        doctor.avatar_url = avatar_url
    if first_name is not None:
        doctor.first_name = first_name
    if last_name is not None:
        doctor.last_name = last_name
    if patronymic is not None:
        doctor.patronymic = patronymic
    if position is not None:
        doctor.position = position
    if description is not None:
        doctor.description = description

    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/{doctor_id}/json", response_model=DoctorResponse)
def update_doctor_json(
    doctor_id: int,
    data: DoctorUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> Doctor:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    doctor_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> None:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
