"""
Database seeding script.

Run this script to populate the database with sample data.

Usage:
    python scripts/seed_database.py [--clear]

Options:
    --clear  Clear existing data before seeding
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from loguru import logger

from app.db.seed import clear_database, seed_database
from app.db.session import AsyncSessionLocal


async def run_seeding(clear_first: bool = False):
    """
    Run database seeding.

    Args:
        clear_first: Whether to clear existing data first
    """
    async with AsyncSessionLocal() as db:
        if clear_first:
            logger.warning("⚠️  Clearing existing data...")
            await clear_database(db)
            logger.info("")

        await seed_database(db)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding",
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_seeding(clear_first=args.clear))
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Seeding cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Seeding failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
