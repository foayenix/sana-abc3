#!/usr/bin/env python3
"""
Database seed script for SANA Health Platform.
Creates sample users, practitioners, services, sessions, and health data.
"""

import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Database and models would be imported from your app
# from app.database import get_db, SessionLocal
# from app.models import User, Practitioner, Service, Session, HealthScore, etc.

# Sample data
SPECIALTIES = [
    "Nutrition",
    "Mental Health",
    "Fitness & Exercise",
    "Sleep Therapy",
    "Stress Management",
    "Holistic Wellness",
    "Physical Therapy",
    "Life Coaching",
]

PRACTITIONERS_DATA = [
    {
        "name": "Dr. Sarah Johnson",
        "title": "Licensed Nutritionist, RD",
        "specialties": ["Nutrition", "Holistic Wellness"],
        "bio": "With over 15 years of experience in clinical nutrition, I help clients develop sustainable eating habits that support their health goals.",
        "hourly_rate": 120.00,
        "avatar": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400",
    },
    {
        "name": "Dr. Michael Chen",
        "title": "Clinical Psychologist, PhD",
        "specialties": ["Mental Health", "Stress Management"],
        "bio": "I specialize in cognitive behavioral therapy and mindfulness-based approaches to help clients manage anxiety and depression.",
        "hourly_rate": 150.00,
        "avatar": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400",
    },
    {
        "name": "Emma Williams",
        "title": "Certified Personal Trainer",
        "specialties": ["Fitness & Exercise", "Physical Therapy"],
        "bio": "I create personalized workout plans that fit your lifestyle and help you achieve your fitness goals safely and effectively.",
        "hourly_rate": 80.00,
        "avatar": "https://images.unsplash.com/photo-1594381898411-846e7d193883?w=400",
    },
    {
        "name": "Dr. James Rodriguez",
        "title": "Sleep Specialist, MD",
        "specialties": ["Sleep Therapy", "Stress Management"],
        "bio": "Board-certified sleep medicine specialist helping patients overcome insomnia and sleep disorders for better health.",
        "hourly_rate": 180.00,
        "avatar": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=400",
    },
    {
        "name": "Lisa Thompson",
        "title": "Certified Life Coach",
        "specialties": ["Life Coaching", "Holistic Wellness"],
        "bio": "I help individuals discover their potential, set meaningful goals, and create balanced lives they love.",
        "hourly_rate": 100.00,
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400",
    },
    {
        "name": "Dr. Amanda Foster",
        "title": "Integrative Medicine Specialist",
        "specialties": ["Holistic Wellness", "Nutrition"],
        "bio": "Combining conventional medicine with evidence-based complementary therapies for whole-person healing.",
        "hourly_rate": 200.00,
        "avatar": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=400",
    },
    {
        "name": "Robert Kim",
        "title": "Physical Therapist, DPT",
        "specialties": ["Physical Therapy", "Fitness & Exercise"],
        "bio": "Specialized in sports rehabilitation and chronic pain management with a focus on movement optimization.",
        "hourly_rate": 130.00,
        "avatar": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400",
    },
    {
        "name": "Dr. Patricia Nguyen",
        "title": "Licensed Therapist, LMFT",
        "specialties": ["Mental Health", "Life Coaching"],
        "bio": "Helping individuals and families navigate life transitions, relationships, and personal growth.",
        "hourly_rate": 140.00,
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400",
    },
]

SERVICES_DATA = [
    {
        "name": "Initial Consultation",
        "description": "Comprehensive assessment and personalized health plan development",
        "duration": 60,
        "price_multiplier": 1.0,
    },
    {
        "name": "Follow-up Session",
        "description": "Progress review and plan adjustments",
        "duration": 30,
        "price_multiplier": 0.5,
    },
    {
        "name": "Intensive Session",
        "description": "Extended deep-dive session for complex issues",
        "duration": 90,
        "price_multiplier": 1.5,
    },
    {
        "name": "Quick Check-in",
        "description": "Brief progress update and guidance",
        "duration": 15,
        "price_multiplier": 0.25,
    },
]

REVIEWS_DATA = [
    {
        "rating": 5,
        "comment": "Absolutely life-changing! I've seen incredible improvements in my health.",
        "reviewer": "John D.",
    },
    {
        "rating": 5,
        "comment": "Very professional and knowledgeable. Highly recommend!",
        "reviewer": "Sarah M.",
    },
    {
        "rating": 4,
        "comment": "Great experience overall. Helped me understand my health better.",
        "reviewer": "Mike R.",
    },
    {
        "rating": 5,
        "comment": "The personalized approach made all the difference.",
        "reviewer": "Emily K.",
    },
    {
        "rating": 4,
        "comment": "Very attentive and caring. Good communication throughout.",
        "reviewer": "David L.",
    },
]

JOURNAL_ENTRY_TYPES = ["symptom", "lifestyle", "achievement", "concern"]

MOOD_NOTES = [
    "Had a great workout today",
    "Feeling stressed about work",
    "Slept well last night",
    "Ate healthy meals",
    "Practiced meditation",
    "Feeling energetic",
    "A bit tired today",
    "Good day overall",
]


def create_sample_users():
    """Create sample user accounts"""
    users = [
        {
            "email": "demo@sana.com",
            "password": "demo123",  # Should be hashed
            "full_name": "Demo User",
            "phone": "+1234567890",
            "date_of_birth": "1990-05-15",
            "health_goals": ["Improve nutrition", "Manage stress", "Better sleep"],
        },
        {
            "email": "test@sana.com",
            "password": "test123",
            "full_name": "Test User",
            "phone": "+1987654321",
            "date_of_birth": "1985-08-22",
            "health_goals": ["Lose weight", "Build muscle", "Increase energy"],
        },
    ]
    return users


def create_practitioners():
    """Create practitioner accounts with services"""
    practitioners = []
    for i, data in enumerate(PRACTITIONERS_DATA):
        practitioner = {
            **data,
            "id": i + 1,
            "email": f"practitioner{i+1}@sana.com",
            "is_verified": True,
            "rating": round(random.uniform(4.0, 5.0), 1),
            "total_reviews": random.randint(10, 100),
            "success_rate": random.randint(85, 99),
        }

        # Add services for each practitioner
        practitioner["services"] = []
        for j, service in enumerate(SERVICES_DATA):
            practitioner["services"].append({
                "id": i * len(SERVICES_DATA) + j + 1,
                "name": service["name"],
                "description": service["description"],
                "duration": service["duration"],
                "price": round(data["hourly_rate"] * service["price_multiplier"], 2),
            })

        # Add reviews
        practitioner["reviews"] = []
        for k in range(random.randint(3, 5)):
            review = random.choice(REVIEWS_DATA)
            practitioner["reviews"].append({
                "rating": review["rating"],
                "comment": review["comment"],
                "reviewer_name": review["reviewer"],
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            })

        practitioners.append(practitioner)

    return practitioners


def create_sample_sessions(user_id: int, practitioners: list):
    """Create sample sessions for a user"""
    sessions = []

    # Past completed sessions
    for i in range(3):
        practitioner = random.choice(practitioners)
        service = random.choice(practitioner["services"])
        sessions.append({
            "user_id": user_id,
            "practitioner_id": practitioner["id"],
            "service_id": service["id"],
            "scheduled_at": (datetime.now() - timedelta(days=random.randint(7, 30))).isoformat(),
            "duration": service["duration"],
            "status": "completed",
            "price": service["price"],
            "notes": "Thank you for a great session!",
        })

    # Upcoming sessions
    for i in range(2):
        practitioner = random.choice(practitioners)
        service = random.choice(practitioner["services"])
        sessions.append({
            "user_id": user_id,
            "practitioner_id": practitioner["id"],
            "service_id": service["id"],
            "scheduled_at": (datetime.now() + timedelta(days=random.randint(1, 14))).isoformat(),
            "duration": service["duration"],
            "status": "scheduled",
            "price": service["price"],
            "notes": "",
        })

    return sessions


def create_sample_health_data(user_id: int):
    """Create sample health tracking data"""
    health_data = {
        "health_score": {
            "score": random.randint(65, 85),
            "dimensions": {
                "physical": random.randint(60, 90),
                "mental": random.randint(60, 90),
                "nutrition": random.randint(60, 90),
                "sleep": random.randint(60, 90),
                "stress": random.randint(60, 90),
            },
        },
        "journal_entries": [],
        "mood_history": [],
    }

    # Create journal entries
    for i in range(5):
        entry_type = random.choice(JOURNAL_ENTRY_TYPES)
        health_data["journal_entries"].append({
            "entry_type": entry_type,
            "title": f"Sample {entry_type.title()} Entry",
            "description": f"This is a sample {entry_type} entry for testing purposes.",
            "severity": random.randint(1, 5) if entry_type in ["symptom", "concern"] else None,
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 14))).isoformat(),
        })

    # Create mood history for past 7 days
    for i in range(7):
        health_data["mood_history"].append({
            "mood_score": random.randint(2, 5),
            "energy_level": random.randint(1, 5),
            "stress_level": random.randint(1, 5),
            "notes": random.choice(MOOD_NOTES),
            "created_at": (datetime.now() - timedelta(days=i)).isoformat(),
        })

    return health_data


def create_sample_conversations(user_id: int, practitioners: list):
    """Create sample conversations with messages"""
    conversations = []

    # Create conversations with 2-3 practitioners
    for practitioner in practitioners[:3]:
        messages = [
            {
                "sender_id": user_id,
                "content": "Hi, I have a question about my treatment plan.",
                "created_at": (datetime.now() - timedelta(hours=48)).isoformat(),
            },
            {
                "sender_id": practitioner["id"],
                "content": "Hello! Of course, I'm happy to help. What would you like to know?",
                "created_at": (datetime.now() - timedelta(hours=47)).isoformat(),
            },
            {
                "sender_id": user_id,
                "content": "I was wondering about the recommended exercises.",
                "created_at": (datetime.now() - timedelta(hours=24)).isoformat(),
            },
            {
                "sender_id": practitioner["id"],
                "content": "Great question! I'll send you a detailed guide shortly.",
                "created_at": (datetime.now() - timedelta(hours=23)).isoformat(),
            },
        ]

        conversations.append({
            "user_id": user_id,
            "practitioner_id": practitioner["id"],
            "practitioner_name": practitioner["name"],
            "messages": messages,
            "unread_count": random.randint(0, 2),
        })

    return conversations


def generate_time_slots():
    """Generate available time slots for practitioners"""
    slots = []
    base_times = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

    for time in base_times:
        slots.append({
            "time": time,
            "available": random.choice([True, True, True, False]),  # 75% availability
        })

    return slots


async def seed_database():
    """Main function to seed the database"""
    print("🌱 Starting database seeding...")

    # Create users
    users = create_sample_users()
    print(f"✅ Created {len(users)} sample users")

    # Create practitioners
    practitioners = create_practitioners()
    print(f"✅ Created {len(practitioners)} practitioners with services")

    # Create sessions for demo user
    sessions = create_sample_sessions(user_id=1, practitioners=practitioners)
    print(f"✅ Created {len(sessions)} sample sessions")

    # Create health data
    health_data = create_sample_health_data(user_id=1)
    print(f"✅ Created health score and {len(health_data['journal_entries'])} journal entries")

    # Create conversations
    conversations = create_sample_conversations(user_id=1, practitioners=practitioners)
    print(f"✅ Created {len(conversations)} sample conversations")

    print("\n🎉 Database seeding completed!")
    print("\n📋 Demo Credentials:")
    print("   Email: demo@sana.com")
    print("   Password: demo123")

    return {
        "users": users,
        "practitioners": practitioners,
        "sessions": sessions,
        "health_data": health_data,
        "conversations": conversations,
    }


def export_to_json(data: dict, filename: str = "seed_data.json"):
    """Export seed data to JSON file for inspection"""
    import json

    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"📄 Seed data exported to {filename}")


if __name__ == "__main__":
    # Run the seeding
    data = asyncio.run(seed_database())

    # Optionally export to JSON
    export_to_json(data)
