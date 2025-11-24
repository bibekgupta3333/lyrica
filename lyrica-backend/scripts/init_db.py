#!/usr/bin/env python
"""
Initialize database and create initial migration.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging, logger
from app.db.session import engine, init_db
from app.db.base import Base


async def init_database():
    """Initialize database tables."""
    setup_logging()
    
    logger.info("Initializing database...")
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database initialized successfully!")
        logger.info(f"Created tables: {', '.join(Base.metadata.tables.keys())}")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())

