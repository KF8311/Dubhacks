from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.ids import new_id
from app.services.llm_guard import openai_chat_payload, settle_probe_reply

_SANDBOX = "Sandbox — simulated Visa Intelligent Commerce flow."


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or new_id("req")


def _envelope(code: str, message: str, request_id: str, details: dict | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id,
        }
    }


def _checkout_probe_path(request: Request) -> bool:
    path = request.url.path.rstrip("/")
    return request.method == "POST" and path.endswith("/checkout")


async def _openai_probe_fallback(request: Request) -> JSONResponse:
    body = (await request.body()).decode("utf-8", errors="replace")
    result = settle_probe_reply(body, None)
    return JSONResponse(
        openai_chat_payload(result.text, refused=result.refused, sandbox_label=_SANDBOX)
    )


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, _request_id(request), exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        if _checkout_probe_path(request):
            return await _openai_probe_fallback(request)
        return JSONResponse(
            status_code=422,
            content=_envelope("VALIDATION_ERROR", "Request validation failed", _request_id(request), {"errors": exc.errors()}),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if _checkout_probe_path(request) and exc.status_code in {400, 415, 422}:
            return await _openai_probe_fallback(request)
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope("HTTP_ERROR", str(exc.detail), _request_id(request)),
        )
