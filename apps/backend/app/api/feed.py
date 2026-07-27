from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.api.dependencies import get_database_session
from app.domain.engagement.schemas import CommentCreate, CommentPage, CommentResponse
from app.domain.engagement.service import EngagementError, EngagementService
from app.domain.feed.schemas import PostCreate, PostPage, PostResponse
from app.domain.feed.service import FeedError, FeedService
from app.domain.identity.models import User

router = APIRouter(tags=["feed"])


def fail(error: FeedError | EngagementError) -> HTTPException:
    return HTTPException(error.status_code, error.message)


@router.get("/feed", response_model=PostPage)
async def feed(
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> PostPage:
    try:
        return await FeedService(db).list(user.id, cursor, limit)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@router.get("/users/{user_id}/posts", response_model=PostPage)
async def profile_posts(
    user_id: UUID,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> PostPage:
    try:
        return await FeedService(db).list(user.id, cursor, limit, user_id)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


@router.post("/feed/posts", response_model=PostResponse, status_code=201)
@router.post("/posts", response_model=PostResponse, status_code=201, include_in_schema=False)
async def create(
    payload: PostCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> PostResponse:
    try:
        return await FeedService(db).create(user.id, payload)
    except FeedError as error:
        raise fail(error) from error


@router.get("/feed/{post_id}", response_model=PostResponse)
@router.get("/posts/{post_id}", response_model=PostResponse, include_in_schema=False)
async def get(
    post_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> PostResponse:
    try:
        return await FeedService(db).get(post_id, user.id)
    except FeedError as error:
        raise fail(error) from error


@router.delete("/feed/{post_id}", status_code=204)
@router.delete("/posts/{post_id}", status_code=204, include_in_schema=False)
async def delete(
    post_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await FeedService(db).delete(post_id, user.id)
    except FeedError as error:
        raise fail(error) from error
    return Response(status_code=204)


@router.post("/feed/{post_id}/likes", status_code=204)
async def like(
    post_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await EngagementService(db).like(post_id, user.id)
    except EngagementError as error:
        raise fail(error) from error
    return Response(status_code=204)


@router.delete("/feed/{post_id}/likes", status_code=204)
async def unlike(
    post_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await EngagementService(db).unlike(post_id, user.id)
    except EngagementError as error:
        raise fail(error) from error
    return Response(status_code=204)


@router.get("/feed/{post_id}/comments", response_model=CommentPage)
async def comments(
    post_id: UUID,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> CommentPage:
    try:
        return await EngagementService(db).comments(post_id, user.id, cursor, limit)
    except (EngagementError, ValueError) as error:
        if isinstance(error, EngagementError):
            raise fail(error) from error
        raise HTTPException(422, str(error)) from error


@router.post("/feed/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> CommentResponse:
    try:
        return await EngagementService(db).create_comment(post_id, user.id, payload)
    except EngagementError as error:
        raise fail(error) from error


@router.delete("/feed/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_database_session),
) -> Response:
    try:
        await EngagementService(db).delete_comment(comment_id, user.id)
    except EngagementError as error:
        raise fail(error) from error
    return Response(status_code=204)
