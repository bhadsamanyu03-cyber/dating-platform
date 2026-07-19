from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.feed.schemas import PostCreate, PostPage, PostResponse
from app.domain.feed.service import FeedError, FeedService
from app.domain.identity.models import User

router = APIRouter(tags=["feed"])


def fail(error: FeedError):
    return HTTPException(error.status_code, error.message)


@router.get("/feed", response_model=PostPage)
async def feed(db: AsyncSession = Depends(get_database_session)):
    return await FeedService(db).list(None)


@router.get("/users/{user_id}/posts", response_model=PostPage)
async def profile_posts(user_id: UUID, db: AsyncSession = Depends(get_database_session)):
    return await FeedService(db).list(None, user_id)


@router.post("/posts", response_model=PostResponse, status_code=201)
async def create(
    payload: PostCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await FeedService(db).create(user.id, payload)
    except FeedError as error:
        raise fail(error) from error


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get(
    post_id: UUID,
    user: User | None = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        return await FeedService(db).get(post_id, user.id if user else None)
    except FeedError as error:
        raise fail(error) from error


@router.delete("/posts/{post_id}", status_code=204)
async def delete(
    post_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
):
    try:
        await FeedService(db).delete(post_id, user.id)
    except FeedError as error:
        raise fail(error) from error
    return Response(status_code=204)
