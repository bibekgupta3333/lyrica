"""
Database seeding utilities.

This module provides functions to seed the database with sample data
for development and testing.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.api_key import APIKey
from app.models.feedback import UserFeedback
from app.models.lyrics import Lyrics, LyricsSection
from app.models.user import User

# ============================================================================
# User Seeding
# ============================================================================


async def seed_users(db: AsyncSession) -> list[User]:
    """
    Seed sample users.

    Creates admin and regular users for testing.

    Args:
        db: Database session

    Returns:
        List of created users
    """
    logger.info("Seeding users...")

    users_data = [
        {
            "email": "admin@lyrica.com",
            "username": "admin",
            "password": "Admin123!",
            "full_name": "Admin User",
            "role": "admin",
            "is_verified": True,
        },
        {
            "email": "demo@lyrica.com",
            "username": "demouser",
            "password": "Demo123!",
            "full_name": "Demo User",
            "role": "user",
            "is_verified": True,
        },
        {
            "email": "artist@lyrica.com",
            "username": "artist1",
            "password": "Artist123!",
            "full_name": "Artist User",
            "role": "user",
            "is_verified": True,
        },
    ]

    users = []
    for user_data in users_data:
        password = user_data.pop("password")
        user = User(
            **user_data,
            password_hash=get_password_hash(password),
            is_active=True,
        )
        db.add(user)
        users.append(user)
        logger.info(f"  → Created user: {user.email}")

    await db.commit()

    # Refresh to get IDs
    for user in users:
        await db.refresh(user)

    logger.success(f"✅ Seeded {len(users)} users")
    return users


# ============================================================================
# Lyrics Seeding
# ============================================================================


async def seed_lyrics(db: AsyncSession, users: list[User]) -> list[Lyrics]:
    """
    Seed sample lyrics.

    Args:
        db: Database session
        users: List of users to assign lyrics to

    Returns:
        List of created lyrics
    """
    logger.info("Seeding lyrics...")

    lyrics_data = [
        {
            "title": "Sunshine Dreams",
            "content": """[Verse 1]
Walking down the street on a sunny day
Feeling all my worries fade away
The sky is blue, the birds they sing
Life is good, it's a beautiful thing

[Chorus]
Sunshine dreams, lighting up my way
Every moment feels like a holiday
With you by my side, everything's right
Sunshine dreams, shining so bright

[Verse 2]
Dancing through the city lights
Everything just feels so right
Your smile lights up the darkest night
Together we'll take flight

[Chorus]
Sunshine dreams, lighting up my way
Every moment feels like a holiday
With you by my side, everything's right
Sunshine dreams, shining so bright

[Bridge]
And when the rain comes falling down
We'll dance until we're homeward bound
No storm can break our golden crown
Love lifts us off the ground

[Chorus]
Sunshine dreams, lighting up my way
Every moment feels like a holiday
With you by my side, everything's right
Sunshine dreams, shining so bright""",
            "structure": {
                "sections": [
                    {"type": "verse", "number": 1},
                    {"type": "chorus", "number": 1},
                    {"type": "verse", "number": 2},
                    {"type": "chorus", "number": 2},
                    {"type": "bridge", "number": 1},
                    {"type": "chorus", "number": 3},
                ]
            },
            "genre": "pop",
            "mood": "happy",
            "theme": "joy",
            "is_public": True,
            "quality_score": 8.5,
        },
        {
            "title": "Midnight Thoughts",
            "content": """[Verse 1]
Lying in the darkness, thoughts running wild
Memories of yesterday, when I was just a child
The clock keeps ticking, but time stands still
Searching for answers on this endless hill

[Chorus]
Midnight thoughts, they haunt my mind
Looking for the truth I need to find
In the silence, whispers call my name
Nothing's ever going to be the same

[Verse 2]
Shadows dance across my wall
Echoes of a distant call
Questions linger, answers fade
In this midnight masquerade

[Chorus]
Midnight thoughts, they haunt my mind
Looking for the truth I need to find
In the silence, whispers call my name
Nothing's ever going to be the same""",
            "structure": {
                "sections": [
                    {"type": "verse", "number": 1},
                    {"type": "chorus", "number": 1},
                    {"type": "verse", "number": 2},
                    {"type": "chorus", "number": 2},
                ]
            },
            "genre": "indie",
            "mood": "melancholic",
            "theme": "reflection",
            "is_public": True,
            "quality_score": 8.0,
        },
        {
            "title": "Rise Up",
            "content": """[Verse 1]
When the world tries to bring you down
Stand tall, don't let them see you frown
You've got the fire burning inside
Let it show, don't let it hide

[Chorus]
Rise up, rise up, reach for the sky
Spread your wings and learn to fly
No chains can hold you, you're breaking free
Rise up and be who you're meant to be

[Verse 2]
Every scar tells a story of strength
You've come so far, gone the length
Warriors don't break, they bend
This is not the end, just a new trend

[Chorus]
Rise up, rise up, reach for the sky
Spread your wings and learn to fly
No chains can hold you, you're breaking free
Rise up and be who you're meant to be

[Bridge]
They said you couldn't make it
But you proved them wrong
This is your moment
Time to be strong

[Chorus]
Rise up, rise up, reach for the sky
Spread your wings and learn to fly
No chains can hold you, you're breaking free
Rise up and be who you're meant to be""",
            "structure": {
                "sections": [
                    {"type": "verse", "number": 1},
                    {"type": "chorus", "number": 1},
                    {"type": "verse", "number": 2},
                    {"type": "chorus", "number": 2},
                    {"type": "bridge", "number": 1},
                    {"type": "chorus", "number": 3},
                ]
            },
            "genre": "rock",
            "mood": "energetic",
            "theme": "empowerment",
            "is_public": True,
            "quality_score": 9.0,
        },
        {
            "title": "Ocean Waves",
            "content": """[Verse 1]
Sitting by the ocean, watching waves roll in
Salt air and serenity, where do I begin
The rhythm of the water, it calms my soul
In this peaceful moment, I feel whole

[Chorus]
Ocean waves, wash away my fears
Carry me through all these years
Endless blue horizon, calling me home
Ocean waves, I'm never alone

[Verse 2]
Footprints in the sand, washed away by tide
Lessons that the ocean tries to confide
Let go of the past, embrace what's new
Life flows like water, pure and true

[Chorus]
Ocean waves, wash away my fears
Carry me through all these years
Endless blue horizon, calling me home
Ocean waves, I'm never alone""",
            "structure": {
                "sections": [
                    {"type": "verse", "number": 1},
                    {"type": "chorus", "number": 1},
                    {"type": "verse", "number": 2},
                    {"type": "chorus", "number": 2},
                ]
            },
            "genre": "acoustic",
            "mood": "peaceful",
            "theme": "nature",
            "is_public": True,
            "quality_score": 8.7,
        },
        {
            "title": "City Nights",
            "content": """[Verse 1]
Neon lights flashing, city comes alive
People rushing past, just trying to survive
Concrete jungle, steel and glass
Every moment speeding past

[Chorus]
City nights, never sleep, always bright
Lost in the rhythm of the night
A million stories in this place
City nights, setting the pace

[Verse 2]
Taxi cabs and subway trains
Money, power, pleasure, pains
Skyscrapers touching the stars
Dreams hiding behind closed doors

[Chorus]
City nights, never sleep, always bright
Lost in the rhythm of the night
A million stories in this place
City nights, setting the pace""",
            "structure": {
                "sections": [
                    {"type": "verse", "number": 1},
                    {"type": "chorus", "number": 1},
                    {"type": "verse", "number": 2},
                    {"type": "chorus", "number": 2},
                ]
            },
            "genre": "hip-hop",
            "mood": "urban",
            "theme": "city-life",
            "is_public": True,
            "quality_score": 7.8,
        },
    ]

    lyrics_list = []
    for idx, lyrics_dict in enumerate(lyrics_data):
        # Assign to users in round-robin
        user = users[idx % len(users)]

        lyrics = Lyrics(**lyrics_dict, user_id=user.id)

        db.add(lyrics)
        lyrics_list.append(lyrics)
        logger.info(f"  → Created lyrics: {lyrics.title} (by {user.username})")

    await db.commit()

    # Refresh to get IDs
    for lyrics in lyrics_list:
        await db.refresh(lyrics)

    logger.success(f"✅ Seeded {len(lyrics_list)} lyrics")
    return lyrics_list


# ============================================================================
# Feedback Seeding
# ============================================================================


async def seed_feedback(
    db: AsyncSession, users: list[User], lyrics_list: list[Lyrics]
) -> list[UserFeedback]:
    """
    Seed sample feedback.

    Args:
        db: Database session
        users: List of users
        lyrics_list: List of lyrics to give feedback on

    Returns:
        List of created feedback
    """
    logger.info("Seeding feedback...")

    feedback_data = [
        {
            "quality_rating": 5,
            "creativity_rating": 5,
            "comment": "Amazing lyrics! Really captured the mood perfectly.",
            "tags": ["creative", "emotional", "well-structured"],
        },
        {
            "quality_rating": 4,
            "creativity_rating": 4,
            "comment": "Great work! Minor improvements could be made to the bridge.",
            "tags": ["good-rhymes", "catchy"],
        },
        {
            "quality_rating": 5,
            "creativity_rating": 5,
            "comment": "Absolutely love this! The imagery is beautiful.",
            "tags": ["creative", "inspiring"],
        },
    ]

    feedback_list = []
    for idx, feedback_dict in enumerate(feedback_data):
        # Assign feedback to lyrics
        lyrics = lyrics_list[idx % len(lyrics_list)]
        user = users[(idx + 1) % len(users)]  # Different user than creator

        feedback = UserFeedback(**feedback_dict, user_id=user.id, lyrics_id=lyrics.id)

        db.add(feedback)
        feedback_list.append(feedback)

    await db.commit()

    logger.success(f"✅ Seeded {len(feedback_list)} feedback items")
    return feedback_list


# ============================================================================
# Main Seeding Function
# ============================================================================


async def seed_database(db: AsyncSession):
    """
    Seed database with all sample data.

    Args:
        db: Database session
    """
    logger.info("=" * 80)
    logger.info("DATABASE SEEDING")
    logger.info("=" * 80)
    logger.info("")

    try:
        # 1. Seed users
        users = await seed_users(db)
        logger.info("")

        # 2. Seed lyrics
        lyrics_list = await seed_lyrics(db, users)
        logger.info("")

        # 3. Seed feedback
        feedback_list = await seed_feedback(db, users, lyrics_list)
        logger.info("")

        logger.info("=" * 80)
        logger.success("✅ DATABASE SEEDING COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"  Users: {len(users)}")
        logger.info(f"  Lyrics: {len(lyrics_list)}")
        logger.info(f"  Feedback: {len(feedback_list)}")
        logger.info("")
        logger.info("📝 Test Credentials:")
        logger.info("  Admin: admin@lyrica.com / Admin123!")
        logger.info("  Demo: demo@lyrica.com / Demo123!")
        logger.info("  Artist: artist@lyrica.com / Artist123!")
        logger.info("")

    except Exception as e:
        logger.error(f"❌ Seeding failed: {str(e)}")
        raise


async def clear_database(db: AsyncSession):
    """
    Clear all data from database (DANGER!).

    Args:
        db: Database session
    """
    logger.warning("⚠️  Clearing database...")

    from app.models import feedback, lyrics, user

    await db.execute(feedback.UserFeedback.__table__.delete())
    await db.execute(lyrics.Lyrics.__table__.delete())
    await db.execute(user.User.__table__.delete())

    await db.commit()

    logger.success("✅ Database cleared")


# ============================================================================
# CLI Entry Point
# ============================================================================


async def main():
    """Main entry point for seeding script."""
    async with AsyncSessionLocal() as db:
        await seed_database(db)


if __name__ == "__main__":
    asyncio.run(main())
