import shutil
from datetime import datetime, UTC
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

import svcs
from fastapi import APIRouter, File, Form, Response, status, UploadFile, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from disguisedcats.settings import settings

post_router = APIRouter()


class Post(BaseModel):
    author_id: UUID
    img: Path
    created_at: datetime


class GetPostsRequest(BaseModel):
    from_: list[UUID] = Field(..., alias="from")


@post_router.get("/posts")
async def get_posts(
    services: svcs.fastapi.DepContainer,
    from_: list[UUID] = Query(..., alias="from"),
) -> list[Post]:
    db = await services.aget(AsyncIOMotorClient)
    results = db.posts.find({"author_id": {"$in": from_}})
    response = [Post(**post) async for post in results]
    return response


@post_router.post("/posts")
async def create_post(
    author_id: Annotated[UUID, Form()],
    img: Annotated[UploadFile, File()],
    services: svcs.fastapi.DepContainer,
    response: Response,
) -> Post:
    db = await services.aget(AsyncIOMotorClient)
    post_id = uuid4()
    created_at = datetime.now(UTC)

    img_extension = img.filename.split(".")[-1]
    img_path = f"imgs/{post_id}.{img_extension}"
    img_full_path = settings.STATIC_PATH / img_path
    with open(img_full_path, "wb+") as f:
        shutil.copyfileobj(img.file, f)

    await db.posts.insert_one(
        {
            "_id": post_id,
            "author_id": author_id,
            "img": img_path,
            "created_at": created_at,
        }
    )

    response.status = status.HTTP_201_CREATED
    return Post(author_id=author_id, img=img_path, created_at=created_at)
