"""
Dummy data generator for SANA Algorithms Suite testing.
"""

import random
from typing import List, Dict
from uuid import uuid4
from datetime import datetime, timedelta

from models.user import User, UserProfile
from models.practitioner import Practitioner
from models.intervention import Intervention
from models.health_data import HealthScore


def generate_dummy_user() -> User:
    """Generate a dummy user for testing."""
    return User(
        id=uuid4(),
        email=f"user_{random.randint(1000, 9999)}@example.com",
        full_name=random.choice([
            "Alice Johnson", "Bob Smith", "Carol Williams",
            "David Brown", "Eva Martinez", "Frank Lee"
        ]),
        age=random.randint(25, 65)
    )


def generate_dummy_profile(user_id) -> UserProfile:
    """Generate a dummy user profile."""
    return UserProfile(
        user_id=user_id,
        preferences={
            "preferred_modalities": random.sample(
                ["yoga", "meditation", "herbal", "acupuncture", "massage"],
                k=2
            ),
            "time_preference": random.choice(["morning", "afternoon", "evening"])
        },
        health_goals=random.sample([
            "reduce_stress", "improve_sleep", "increase_energy",
            "manage_pain", "boost_immunity", "improve_focus"
        ], k=3),
        budget_weekly=random.choice([50, 100, 150, 200, 250]),
        time_available_weekly=random.choice([60, 120, 180, 240])
    )


def generate_dummy_practitioner() -> Practitioner:
    """Generate a dummy practitioner for testing."""
    specialties = random.sample([
        "Acupuncture", "Yoga", "Meditation", "Herbal Medicine",
        "Ayurveda", "Naturopathy", "Massage Therapy", "Reiki"
    ], k=random.randint(1, 3))

    credentials = random.sample([
        "RYT-200", "L.Ac", "ND", "RMT", "NCCAOM", "CNHP"
    ], k=random.randint(1, 2))

    return Practitioner(
        id=uuid4(),
        full_name=random.choice([
            "Dr. Sarah Chen", "John Williams, L.Ac",
            "Maria Garcia, ND", "James Kim, RMT"
        ]),
        specialties=specialties,
        credentials=credentials,
        verified=random.choice([True, False]),
        sana_index_score=round(random.uniform(60, 95), 1),
        hourly_rate=random.choice([75, 100, 125, 150, 200])
    )


def generate_dummy_questionnaire_responses() -> Dict[str, Dict[str, int]]:
    """Generate dummy questionnaire responses for all domains."""
    domains = ["physical", "emotional", "social", "cognitive", "spiritual"]
    responses = {}

    for domain in domains:
        responses[domain] = {
            f"q{i}": random.randint(20, 100)
            for i in range(1, 6)
        }

    return responses


def generate_dummy_health_score(user_id) -> HealthScore:
    """Generate a dummy health score for testing."""
    domain_scores = {
        "physical": round(random.uniform(40, 90), 1),
        "emotional": round(random.uniform(40, 90), 1),
        "social": round(random.uniform(40, 90), 1),
        "cognitive": round(random.uniform(40, 90), 1),
        "spiritual": round(random.uniform(40, 90), 1)
    }

    # Calculate weighted overall
    weights = {
        "physical": 0.25,
        "emotional": 0.25,
        "social": 0.15,
        "cognitive": 0.20,
        "spiritual": 0.15
    }
    overall = sum(score * weights[domain] for domain, score in domain_scores.items())

    return HealthScore(
        id=uuid4(),
        user_id=user_id,
        overall_score=round(overall, 1),
        domain_scores=domain_scores
    )


def generate_dummy_intervention() -> Intervention:
    """Generate a dummy intervention for testing."""
    categories = {
        "yoga": ["Hatha Yoga", "Vinyasa Flow", "Yin Yoga", "Restorative Yoga"],
        "meditation": ["Mindfulness", "Guided Meditation", "Body Scan", "Loving Kindness"],
        "herbal": ["Ashwagandha", "Turmeric", "Valerian", "Rhodiola"],
        "acupuncture": ["Traditional Acupuncture", "Auricular", "Electroacupuncture"],
        "massage": ["Swedish Massage", "Deep Tissue", "Trigger Point", "Shiatsu"]
    }

    category = random.choice(list(categories.keys()))
    name = random.choice(categories[category])

    return Intervention(
        id=uuid4(),
        name=name,
        category=category,
        evidence_rating=random.choice(["strong", "moderate", "weak"]),
        target_domains=random.sample(
            ["physical", "emotional", "social", "cognitive", "spiritual"],
            k=random.randint(1, 3)
        ),
        contraindications=random.sample(
            ["pregnancy", "bleeding_disorders", "heart_conditions", "none"],
            k=random.randint(0, 2)
        ),
        typical_duration_minutes=random.choice([15, 30, 45, 60, 90]),
        cost_estimate=random.choice([20, 40, 60, 80, 100])
    )
