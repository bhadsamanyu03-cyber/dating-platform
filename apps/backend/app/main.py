from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from app.api.router import router
from app.api.auth import router as auth_router
from app.api.profile import interests_router, profile_router
from app.api.discovery import router as discovery_router
from app.api.matches import router as matches_router
from app.api.media import router as media_router
from app.api.conversations import message_router, router as conversations_router
from app.api.feed import router as feed_router
from app.api.search import router as search_router
from app.api.notifications import router as notifications_router
from app.api.reports import router as reports_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.database import create_database_engine
from app.infrastructure.redis import create_redis_client
from app.infrastructure.email import DevelopmentEmailProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.app_log_level)
    app.state.db_engine = create_database_engine(str(settings.database_url))
    app.state.redis = create_redis_client(str(settings.redis_url))
    app.state.email_provider = DevelopmentEmailProvider()
    yield
    await app.state.redis.aclose()
    await app.state.db_engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(x) for x in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(profile_router, prefix=settings.api_prefix)
    app.include_router(interests_router, prefix=settings.api_prefix)
    app.include_router(discovery_router, prefix=settings.api_prefix)
    app.include_router(matches_router, prefix=settings.api_prefix)
    app.include_router(media_router, prefix=settings.api_prefix)
    app.include_router(conversations_router, prefix=settings.api_prefix)
    app.include_router(message_router, prefix=settings.api_prefix)
    app.include_router(feed_router, prefix=settings.api_prefix)
    app.include_router(search_router, prefix=settings.api_prefix)
    app.include_router(notifications_router, prefix=settings.api_prefix)
    app.include_router(reports_router, prefix=settings.api_prefix)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_, __):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()
