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
from api.routes import scoring, evidence, planning, verification, matching, safety, learning, herbs, auth, journal, outcomes, practice, marketplace, payments, messaging, analytics, wearables, enterprise, widget, scanner, ai_assistant, marketplace_products, freemium
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

app.include_router(
    marketplace.router,
    prefix=f"{settings.API_V1_PREFIX}/marketplace",
    tags=["marketplace"]
)

app.include_router(
    payments.router,
    prefix=f"{settings.API_V1_PREFIX}/payments",
    tags=["payments"]
)

app.include_router(
    messaging.router,
    prefix=f"{settings.API_V1_PREFIX}/messaging",
    tags=["messaging"]
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["analytics"]
)

app.include_router(
    wearables.router,
    prefix=f"{settings.API_V1_PREFIX}/wearables",
    tags=["wearables"]
)

app.include_router(
    enterprise.router,
    prefix=f"{settings.API_V1_PREFIX}/enterprise",
    tags=["enterprise"]
)

app.include_router(
    widget.router,
    prefix=f"{settings.API_V1_PREFIX}/widget",
    tags=["widget"]
)

app.include_router(
    scanner.router,
    prefix=f"{settings.API_V1_PREFIX}/scanner",
    tags=["scanner"]
)

app.include_router(
    ai_assistant.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["ai-assistant"]
)

app.include_router(
    marketplace_products.router,
    prefix=f"{settings.API_V1_PREFIX}/marketplace-products",
    tags=["marketplace-products"]
)

app.include_router(
    freemium.router,
    prefix=f"{settings.API_V1_PREFIX}/freemium",
    tags=["freemium"]
)
