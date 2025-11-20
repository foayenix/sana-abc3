"""
Simplified SANA API for quick testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="SANA Algorithms Suite", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://0.0.0.0:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "SANA Algorithms Suite API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/scoring/test-full-flow")
async def test_full_flow(profile: str = "balanced"):
    """Test endpoint for scoring"""

    # Generate dummy scores based on profile
    if profile == "balanced":
        base_score = 70
    elif profile == "struggling":
        base_score = 45
    elif profile == "thriving":
        base_score = 90
    else:
        base_score = 65

    # Add some randomness
    overall_score = base_score + random.randint(-5, 5)

    domain_scores = {
        "physical": {
            "raw_score": overall_score + random.randint(-10, 10),
            "normalized_score": overall_score + random.randint(-10, 10)
        },
        "emotional": {
            "raw_score": overall_score + random.randint(-10, 10),
            "normalized_score": overall_score + random.randint(-10, 10)
        },
        "social": {
            "raw_score": overall_score + random.randint(-10, 10),
            "normalized_score": overall_score + random.randint(-10, 10)
        },
        "cognitive": {
            "raw_score": overall_score + random.randint(-10, 10),
            "normalized_score": overall_score + random.randint(-10, 10)
        },
        "spiritual": {
            "raw_score": overall_score + random.randint(-10, 10),
            "normalized_score": overall_score + random.randint(-10, 10)
        }
    }

    # Find weak domains (below 60)
    weak_domains = [
        domain for domain, scores in domain_scores.items()
        if scores["normalized_score"] < 60
    ]

    return {
        "overall_score": overall_score,
        "domain_scores": domain_scores,
        "weak_domains": weak_domains,
        "profile_used": profile
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
