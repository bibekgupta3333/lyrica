"""
Song Generation Readiness Verification Script

Comprehensive check to verify if the system is ready for song generation.

Usage:
    python scripts/verify_generation_readiness.py
"""

import asyncio
import sys
from pathlib import Path

from loguru import logger
from sqlalchemy.future import select

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.lyrics import Lyrics
from app.models.user import User
from app.models.voice_profile import VoiceProfile


class ReadinessChecker:
    """Check system readiness for song generation."""

    def __init__(self):
        """Initialize checker."""
        self.checks_passed = 0
        self.checks_total = 0
        self.warnings = []
        self.errors = []

    async def run_all_checks(self):
        """Run all readiness checks."""
        logger.info("=" * 80)
        logger.info("SONG GENERATION READINESS CHECK")
        logger.info("=" * 80)
        logger.info("")

        async with AsyncSessionLocal() as db:
            # 1. Database Connection
            await self._check_database_connection(db)

            # 2. Users
            user_count = await self._check_users(db)

            # 3. Voice Profiles
            voice_count = await self._check_voice_profiles(db)

            # 4. Lyrics
            lyrics_count = await self._check_lyrics(db)

            # 5. ChromaDB
            chromadb_count = await self._check_chromadb()

            # 6. RAG Search
            if chromadb_count > 0:
                await self._check_rag_search()

            # 7. Voice Synthesis
            await self._check_voice_synthesis()

            # 8. Music Generation
            await self._check_music_generation()

        # Print Summary
        self._print_summary(user_count, voice_count, lyrics_count, chromadb_count)

    async def _check_database_connection(self, db):
        """Check database connection."""
        self.checks_total += 1
        logger.info("1. Database Connection")
        try:
            await db.execute(select(User).limit(1))
            logger.success("   ✅ Database connection: OK")
            self.checks_passed += 1
        except Exception as e:
            logger.error(f"   ❌ Database connection: FAILED - {e}")
            self.errors.append("Database connection failed")
        logger.info("")

    async def _check_users(self, db):
        """Check users."""
        self.checks_total += 1
        logger.info("2. Users")
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()
            count = len(users)

            if count >= 1:
                logger.success(f"   ✅ Users found: {count}")
                self.checks_passed += 1
                # Show users
                for user in users[:5]:
                    logger.info(f"      - {user.email} ({user.role})")
            else:
                logger.error("   ❌ No users found")
                self.errors.append("At least 1 user required")

            return count

        except Exception as e:
            logger.error(f"   ❌ User check failed: {e}")
            self.errors.append("User check failed")
            return 0
        finally:
            logger.info("")

    async def _check_voice_profiles(self, db):
        """Check voice profiles."""
        self.checks_total += 1
        logger.info("3. Voice Profiles")
        try:
            result = await db.execute(select(VoiceProfile))
            profiles = result.scalars().all()
            count = len(profiles)

            if count >= 4:
                logger.success(f"   ✅ Voice profiles found: {count}")
                self.checks_passed += 1
                # Show profiles
                for profile in profiles:
                    status = "✓" if profile.is_available else "✗"
                    logger.info(
                        f"      {status} {profile.name} ({profile.gender}, {profile.language})"
                    )
            elif count > 0:
                logger.warning(f"   ⚠️  Only {count} voice profiles found (recommended: 4+)")
                self.warnings.append(f"Only {count} voice profiles (recommended: 4+)")
                for profile in profiles:
                    logger.info(f"      - {profile.name}")
            else:
                logger.error("   ❌ No voice profiles found")
                self.errors.append("At least 4 voice profiles required")

            return count

        except Exception as e:
            logger.error(f"   ❌ Voice profile check failed: {e}")
            self.errors.append("Voice profile check failed")
            return 0
        finally:
            logger.info("")

    async def _check_lyrics(self, db):
        """Check lyrics."""
        self.checks_total += 1
        logger.info("4. Lyrics")
        try:
            result = await db.execute(select(Lyrics))
            lyrics = result.scalars().all()
            count = len(lyrics)

            if count >= 1000:
                logger.success(f"   ✅ Lyrics found: {count} (Optimal for RAG)")
                self.checks_passed += 1
            elif count >= 100:
                logger.success(f"   ✅ Lyrics found: {count} (Good for RAG)")
                logger.info(f"      Recommendation: Add more lyrics (target: 1,000+)")
                self.checks_passed += 1
                self.warnings.append(f"Only {count} lyrics (recommended: 1,000+)")
            elif count > 0:
                logger.warning(f"   ⚠️  Only {count} lyrics found")
                logger.warning("      Generation will work but quality may be limited")
                logger.info("      Recommendation: Add at least 100 lyrics for basic RAG")
                self.warnings.append(f"Only {count} lyrics (minimum: 100)")
            else:
                logger.warning("   ⚠️  No lyrics found")
                logger.info("      System will work but without RAG context")
                logger.info("      Recommendation: Add lyrics for better quality")
                self.warnings.append("No lyrics found (RAG unavailable)")

            # Show genre distribution
            if count > 0:
                genres = {}
                for lyric in lyrics:
                    genre = lyric.genre or "unknown"
                    genres[genre] = genres.get(genre, 0) + 1

                logger.info(f"      Genre distribution:")
                for genre, cnt in sorted(genres.items(), key=lambda x: x[1], reverse=True)[:5]:
                    logger.info(f"        - {genre}: {cnt}")

            return count

        except Exception as e:
            logger.error(f"   ❌ Lyrics check failed: {e}")
            self.errors.append("Lyrics check failed")
            return 0
        finally:
            logger.info("")

    async def _check_chromadb(self):
        """Check ChromaDB."""
        self.checks_total += 1
        logger.info("5. ChromaDB")
        try:
            from app.services.vector_store import VectorStoreService

            vector_store = VectorStoreService()
            count = vector_store.count()

            if count >= 1000:
                logger.success(f"   ✅ ChromaDB documents: {count} (Optimal)")
                self.checks_passed += 1
            elif count >= 100:
                logger.success(f"   ✅ ChromaDB documents: {count} (Good)")
                self.checks_passed += 1
                self.warnings.append(f"Only {count} embeddings (optimal: 1,000+)")
            elif count > 0:
                logger.warning(f"   ⚠️  Only {count} ChromaDB documents")
                logger.info("      Recommendation: Populate more embeddings")
                self.warnings.append(f"Only {count} embeddings (minimum: 100)")
            else:
                logger.warning("   ⚠️  ChromaDB is empty")
                logger.info("      RAG will not work without embeddings")
                logger.info("      Run: python scripts/ingest_data.py")
                self.warnings.append("ChromaDB empty (RAG unavailable)")

            return count

        except Exception as e:
            logger.warning(f"   ⚠️  ChromaDB check failed: {e}")
            logger.info("      Make sure ChromaDB is running (docker-compose up chromadb)")
            self.warnings.append("ChromaDB not accessible")
            return 0
        finally:
            logger.info("")

    async def _check_rag_search(self):
        """Check RAG search functionality."""
        self.checks_total += 1
        logger.info("6. RAG Search")
        try:
            from app.services.vector_store import VectorStoreService

            vector_store = VectorStoreService()
            results = vector_store.search(query="Write a happy love song", n_results=3)

            if results and len(results["documents"]) > 0:
                logger.success(
                    f"   ✅ RAG search working! Retrieved {len(results['documents'])} results"
                )
                self.checks_passed += 1

                # Show top result
                if results["documents"]:
                    first_metadata = results["metadatas"][0] if results["metadatas"] else {}
                    logger.info(
                        f"      Top result: {first_metadata.get('title', 'Unknown')} ({first_metadata.get('genre', 'unknown')})"
                    )
            else:
                logger.warning("   ⚠️  RAG search returned no results")
                self.warnings.append("RAG search returns no results")

        except Exception as e:
            logger.error(f"   ❌ RAG search test failed: {e}")
            self.errors.append("RAG search test failed")
        finally:
            logger.info("")

    async def _check_voice_synthesis(self):
        """Check voice synthesis configuration."""
        self.checks_total += 1
        logger.info("7. Voice Synthesis")
        try:
            from app.core.voice_config import VOICE_PROFILES, get_voice_config

            config = get_voice_config()
            logger.success(f"   ✅ Voice synthesis configured")
            logger.info(f"      Engine: {config.engine.value}")
            logger.info(f"      Available profiles: {len(VOICE_PROFILES)}")
            self.checks_passed += 1

        except Exception as e:
            logger.warning(f"   ⚠️  Voice synthesis check: {e}")
            self.warnings.append("Voice synthesis configuration issue")
        finally:
            logger.info("")

    async def _check_music_generation(self):
        """Check music generation configuration."""
        self.checks_total += 1
        logger.info("8. Music Generation")
        try:
            # Basic check - just verify imports work
            from app.services.music.generation import MusicGenerationService

            logger.success("   ✅ Music generation service available")
            self.checks_passed += 1

        except Exception as e:
            logger.warning(f"   ⚠️  Music generation check: {e}")
            self.warnings.append("Music generation service issue")
        finally:
            logger.info("")

    def _print_summary(self, user_count, voice_count, lyrics_count, chromadb_count):
        """Print final summary."""
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Checks passed: {self.checks_passed}/{self.checks_total}")
        logger.info("")

        # Critical requirements
        logger.info("Critical Requirements:")
        logger.info(
            f"  ✅ Users: {user_count} (required: 1+)"
            if user_count >= 1
            else f"  ❌ Users: {user_count} (required: 1+)"
        )
        logger.info(
            f"  ✅ Voice Profiles: {voice_count} (required: 4+)"
            if voice_count >= 4
            else f"  ❌ Voice Profiles: {voice_count} (required: 4+)"
        )
        logger.info("")

        # Recommended (for quality)
        logger.info("Recommended (for Quality):")
        if lyrics_count >= 1000:
            logger.info(f"  ✅ Lyrics: {lyrics_count} (optimal: 1,000+)")
        elif lyrics_count >= 100:
            logger.info(f"  ⚠️  Lyrics: {lyrics_count} (recommended: 1,000+)")
        else:
            logger.info(f"  ⚠️  Lyrics: {lyrics_count} (minimum: 100)")

        if chromadb_count >= 1000:
            logger.info(f"  ✅ ChromaDB: {chromadb_count} (optimal: 1,000+)")
        elif chromadb_count >= 100:
            logger.info(f"  ⚠️  ChromaDB: {chromadb_count} (recommended: 1,000+)")
        else:
            logger.info(f"  ⚠️  ChromaDB: {chromadb_count} (minimum: 100)")
        logger.info("")

        # Final verdict
        can_generate = user_count >= 1 and voice_count >= 4

        if can_generate and lyrics_count >= 1000 and chromadb_count >= 1000:
            logger.success("✅ STATUS: READY FOR SONG GENERATION (OPTIMAL)")
            logger.info("   System has all required components and optimal data")
        elif can_generate and lyrics_count >= 100 and chromadb_count >= 100:
            logger.success("✅ STATUS: READY FOR SONG GENERATION (GOOD)")
            logger.info("   System has required components and good data coverage")
        elif can_generate:
            logger.success("✅ STATUS: READY FOR SONG GENERATION (BASIC)")
            logger.warning("   System will work but quality may be limited without RAG")
            logger.info("   Recommendation: Run data ingestion")
            logger.info("   Command: python scripts/ingest_data.py")
        else:
            logger.error("❌ STATUS: NOT READY FOR SONG GENERATION")
            logger.info("   Missing critical requirements")
            logger.info("   Command: python scripts/ingest_data.py")

        if self.errors:
            logger.info("")
            logger.error("Errors:")
            for error in self.errors:
                logger.error(f"  - {error}")

        if self.warnings:
            logger.info("")
            logger.warning("Warnings:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")

        logger.info("")
        logger.info("=" * 80)


async def main():
    """Main entry point."""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
    )

    checker = ReadinessChecker()
    await checker.run_all_checks()


if __name__ == "__main__":
    asyncio.run(main())
