from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.api.routes_health import router as health_router
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.core.ids import new_id
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    application = FastAPI(title="Sniff Visa", version=settings.version)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins(),
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(application)

    @application.middleware("http")
    async def attach_request_id(request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or new_id("req")
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    application.include_router(health_router)
    return application


app = create_app()
