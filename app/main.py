from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.router import api_router
from contextlib import asynccontextmanager
from app.core.database import close_all_engines
from app.core.middleware import InternalAuthMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.settings import settings
import traceback
import sys
import os
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_all_engines()


def create_app() -> FastAPI:
    app = FastAPI(title="Kiara", description="Kiara API", lifespan=lifespan)
    app.include_router(api_router, prefix="/api/v1")
    app.add_middleware(InternalAuthMiddleware)
    return app


app = create_app()
if settings.is_production:
    logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.ERROR)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        if not settings.is_production:
            traceback.print_exc()
        logger = logging.getLogger("fastapi")
        if settings.is_production:
            logger.setLevel(logging.INFO)

        tb = traceback.extract_tb(sys.exc_info()[2])
        filename, line_number, function_name, text = tb[-1]
        filename = os.path.basename(filename)
        logger.error(
            f"Error occurred in file {filename} line {line_number} at {function_name}, {exc}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"Unhandled Exception",
                "data": [],
                "error": True,
            },
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if not settings.is_production:
        print(exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Unprocessable Entity",
            "details": exc.errors(),
            "error": True,
        },
    )
