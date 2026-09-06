"""
FastAPI Main Application Entry Point with Global Exception Handlers
===================================================================
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.app.core.config import settings
from backend.app.database.session import engine, Base
from backend.app.api.api_router import api_router
from backend.app.models import entities  # ensure models are registered

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("inventory_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database schema tables on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/initialized.")
    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade AI platform for retail demand forecasting, inventory optimization, and What-If scenario simulations.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Input request body or query parameters failed validation.",
            "details": exc.errors(),
        },
    )


# Global Unhandled Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing the request.",
            "detail": str(exc) if settings.DEBUG else "Please consult application logs.",
        },
    )


# Mount Master API Router
app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
def root():
    """Root redirect / welcome message."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API. Visit /docs for OpenAPI specifications.",
        "documentation": "/docs",
    }
