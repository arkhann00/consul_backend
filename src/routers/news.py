from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_admin
from database import get_db
from models.news import News
from models.user import User
from schemas.news import NewsCreate, NewsResponse, NewsUpdate
from utils.uploads import save_upload

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=list[NewsResponse])
def list_news(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> list[News]:
    return db.query(News).order_by(News.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> News:
    item = db.query(News).filter(News.id == news_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    return item


@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    image_url: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
) -> News:
    image_path = image_url
    if image is not None and image.filename:
        image_path = await save_upload(image, "news")

    item = News(title=title, description=description, image=image_path)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/json", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news_json(
    data: NewsCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> News:
    item = News(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    image_url: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
) -> News:
    item = db.query(News).filter(News.id == news_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")

    if image is not None and image.filename:
        image_url = await save_upload(image, "news")
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    if image_url is not None:
        item.image = image_url

    db.commit()
    db.refresh(item)
    return item


@router.put("/{news_id}/json", response_model=NewsResponse)
def update_news_json(
    news_id: int,
    data: NewsUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> News:
    item = db.query(News).filter(News.id == news_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(
    news_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin)],
) -> None:
    item = db.query(News).filter(News.id == news_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News not found")
    db.delete(item)
    db.commit()
