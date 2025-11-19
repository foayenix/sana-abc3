"""
SANA Algorithms Suite API

FastAPI application entry point for the SANA Health Framework algorithm suite.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="SANA Health Framework Algorithm Suite API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "SANA Algorithms Suite API",
        "version": settings.VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Import routers
from api.routes import scoring, evidence, planning, verification, matching, safety, learning, herbs, auth, journal, outcomes, practice
from api.routes import index as index_router

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["auth"]
)

app.include_router(
    scoring.router,
    prefix=f"{settings.API_V1_PREFIX}/scoring",
    tags=["scoring"]
)

app.include_router(
    evidence.router,
    prefix=f"{settings.API_V1_PREFIX}/evidence",
    tags=["evidence"]
)

app.include_router(
    planning.router,
    prefix=f"{settings.API_V1_PREFIX}/planning",
    tags=["planning"]
)

app.include_router(
    verification.router,
    prefix=f"{settings.API_V1_PREFIX}/verification",
    tags=["verification"]
)

app.include_router(
    matching.router,
    prefix=f"{settings.API_V1_PREFIX}/matching",
    tags=["matching"]
)

app.include_router(
    safety.router,
    prefix=f"{settings.API_V1_PREFIX}/safety",
    tags=["safety"]
)

app.include_router(
    learning.router,
    prefix=f"{settings.API_V1_PREFIX}/learning",
    tags=["learning"]
)

app.include_router(
    herbs.router,
    prefix=f"{settings.API_V1_PREFIX}/herbs",
    tags=["herbs"]
)

app.include_router(
    index_router.router,
    prefix=f"{settings.API_V1_PREFIX}/index",
    tags=["index"]
)

app.include_router(
    journal.router,
    prefix=f"{settings.API_V1_PREFIX}/journal",
    tags=["journal"]
)

app.include_router(
    outcomes.router,
    prefix=f"{settings.API_V1_PREFIX}/outcomes",
    tags=["outcomes"]
)

app.include_router(
    practice.router,
    prefix=f"{settings.API_V1_PREFIX}/practice",
    tags=["practice"]
)
