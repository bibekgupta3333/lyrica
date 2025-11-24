#!/usr/bin/env python
"""
Seed database with sample data for development.
"""

import asyncio
import sys
from pathlib import Path
from faker import Faker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging, logger
from app.db.session import AsyncSessionLocal
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate

fake = Faker()


async def seed_users(db, count: int = 10):
    """Create sample users."""
    logger.info(f"Creating {count} sample users...")
    
    users = []
    for i in range(count):
        user_in = UserCreate(
            email=f"user{i+1}@example.com",
            username=f"user{i+1}",
            password="password123",
            full_name=fake.name(),
        )
        
        # Check if user exists
        existing = await user_crud.get_by_email(db, email=user_in.email)
        if not existing:
            created_user = await user_crud.create(db, obj_in=user_in)
            users.append(created_user)
            logger.info(f"Created user: {created_user.email}")
        else:
            logger.info(f"User already exists: {user_in.email}")
    
    return users


async def seed_database():
    """Seed database with sample data."""
    setup_logging()
    
    logger.info("🌱 Seeding database...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Create admin user
            admin_email = "admin@lyrica.com"
            existing_admin = await user_crud.get_by_email(db, email=admin_email)
            
            if not existing_admin:
                admin_in = UserCreate(
                    email=admin_email,
                    username="admin",
                    password="admin123",
                    full_name="Admin User",
                )
                admin = await user_crud.create(db, obj_in=admin_in)
                # Set as superuser
                admin.is_superuser = True
                admin.is_verified = True
                await db.commit()
                logger.info(f"✅ Created admin user: {admin.email}")
            else:
                logger.info(f"Admin user already exists: {admin_email}")
            
            # Create sample users
            await seed_users(db, count=5)
            
            # TODO: Seed other data
            # - Sample lyrics
            # - Sample documents for RAG
            
            await db.commit()
            
            logger.info("✅ Database seeded successfully!")
            logger.info("")
            logger.info("📝 Test credentials:")
            logger.info("  Admin: admin@lyrica.com / admin123")
            logger.info("  User1: user1@example.com / password123")
            
        except Exception as e:
            logger.error(f"❌ Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())

