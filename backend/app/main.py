"""
FastAPI Main Application Entry Point
====================================
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.database.session import engine, Base
from backend.app.api.api_router import api_router
from backend.app.models import entities  # ensure models are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database schema tables on application startup."""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    # Create DB tables
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")
    yield
    print("Shutting down application...")


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
