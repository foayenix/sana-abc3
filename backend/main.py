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


# Import routers (will add as we build algorithms)
# from api.routes import scoring, matching, verification, safety, engagement, evidence, planning, index
# app.include_router(scoring.router, prefix=f"{settings.API_V1_PREFIX}/scoring", tags=["scoring"])
