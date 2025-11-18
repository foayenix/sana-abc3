"""
Database seed data for SANA Algorithms Suite.
"""

from uuid import uuid4
from datetime import datetime

# Sample users for seeding
SAMPLE_USERS = [
    {
        "id": str(uuid4()),
        "email": "alice@example.com",
        "full_name": "Alice Johnson",
        "age": 35
    },
    {
        "id": str(uuid4()),
        "email": "bob@example.com",
        "full_name": "Bob Smith",
        "age": 42
    },
    {
        "id": str(uuid4()),
        "email": "carol@example.com",
        "full_name": "Carol Williams",
        "age": 28
    }
]

# Sample practitioners for seeding
SAMPLE_PRACTITIONERS = [
    {
        "id": str(uuid4()),
        "full_name": "Dr. Sarah Chen",
        "specialties": ["Acupuncture", "Traditional Chinese Medicine"],
        "credentials": ["L.Ac", "NCCAOM"],
        "verified": True,
        "sana_index_score": 92.5,
        "hourly_rate": 150
    },
    {
        "id": str(uuid4()),
        "full_name": "John Williams, RYT-500",
        "specialties": ["Yoga", "Meditation"],
        "credentials": ["RYT-500", "YACEP"],
        "verified": True,
        "sana_index_score": 88.0,
        "hourly_rate": 80
    },
    {
        "id": str(uuid4()),
        "full_name": "Maria Garcia, ND",
        "specialties": ["Naturopathy", "Herbal Medicine"],
        "credentials": ["ND", "CNHP"],
        "verified": True,
        "sana_index_score": 90.2,
        "hourly_rate": 125
    }
]

# Sample interventions for seeding
SAMPLE_INTERVENTIONS = [
    {
        "id": str(uuid4()),
        "name": "Hatha Yoga",
        "category": "yoga",
        "evidence_rating": "strong",
        "target_domains": ["physical", "emotional", "spiritual"],
        "contraindications": [],
        "typical_duration_minutes": 60,
        "cost_estimate": 20
    },
    {
        "id": str(uuid4()),
        "name": "Mindfulness Meditation",
        "category": "meditation",
        "evidence_rating": "strong",
        "target_domains": ["emotional", "cognitive", "spiritual"],
        "contraindications": [],
        "typical_duration_minutes": 20,
        "cost_estimate": 0
    },
    {
        "id": str(uuid4()),
        "name": "Acupuncture for Stress",
        "category": "acupuncture",
        "evidence_rating": "moderate",
        "target_domains": ["physical", "emotional"],
        "contraindications": ["bleeding_disorders"],
        "typical_duration_minutes": 45,
        "cost_estimate": 80
    },
    {
        "id": str(uuid4()),
        "name": "Ashwagandha Supplementation",
        "category": "herbal",
        "evidence_rating": "moderate",
        "target_domains": ["physical", "emotional", "cognitive"],
        "contraindications": ["pregnancy", "thyroid_conditions"],
        "typical_duration_minutes": 5,
        "cost_estimate": 30
    }
]


def seed_database(db_session):
    """
    Seed the database with sample data.

    Args:
        db_session: Database session
    """
    # TODO: Implement with actual SQLAlchemy models
    print("Seeding database with sample data...")
    print(f"  - {len(SAMPLE_USERS)} users")
    print(f"  - {len(SAMPLE_PRACTITIONERS)} practitioners")
    print(f"  - {len(SAMPLE_INTERVENTIONS)} interventions")
    print("Database seeding complete.")
