"""
Performance tests for data ingestion pipeline.

Tests benchmark:
- Ingestion speed
- Memory usage
- Batch size optimization
- Parallel processing
- Large dataset handling
"""

import asyncio
import os
import time
from unittest.mock import MagicMock, patch

import psutil
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lyrics import Lyrics
from app.services.ingestion.chromadb_population import ChromaDBPopulationService
from app.services.ingestion.huggingface_ingestion import HuggingFaceIngestionService


def generate_mock_dataset(size: int):
    """Generate mock dataset of specified size."""
    return [
        {
            "title": f"Performance Test Song {i}",
            "lyrics": f"[Verse 1]\nPerformance test content {i}\n\n[Chorus]\nTest chorus {i}\n\n"
            * 5,
            "artist": f"Artist {i}",
            "genre": ["pop", "rock", "hip-hop"][i % 3],
        }
        for i in range(size)
    ]


def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


class TestIngestionPerformance:
    """Performance benchmark tests for ingestion."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_ingestion_speed_small_dataset(self, db_session: AsyncSession):
        """Benchmark ingestion speed with small dataset (100 items)."""
        service = HuggingFaceIngestionService()
        mock_data = generate_mock_dataset(100)
        user_id = "perf-test-user"

        start_time = time.time()

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock:
            mock.return_value = mock_data
            result = await service.ingest_from_dataset(
                db=db_session,
                dataset_name="perf-test",
                max_samples=100,
                user_id=user_id,
                batch_size=10,
            )

        duration = time.time() - start_time

        print(f"\n📊 Small Dataset Performance:")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Throughput: {result['inserted']/duration:.2f} items/sec")

        assert result["processed"] == 100
        assert result["errors"] == 0

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_ingestion_speed_medium_dataset(self, db_session: AsyncSession):
        """Benchmark ingestion speed with medium dataset (1000 items)."""
        service = HuggingFaceIngestionService()
        mock_data = generate_mock_dataset(1000)
        user_id = "perf-test-user"

        start_time = time.time()
        start_memory = get_memory_usage()

        with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock:
            mock.return_value = mock_data

            stats = await service.ingest_from_dataset(
                db=db_session,
                dataset_name="perf-test",
                max_samples=1000,
                user_id=user_id,
                batch_size=50,
            )

        end_time = time.time()
        end_memory = get_memory_usage()

        duration = end_time - start_time
        memory_delta = end_memory - start_memory

        # Performance assertions
        assert duration < 60  # Should complete in under 60 seconds
        assert memory_delta < 500  # Should use less than 500MB additional memory
        assert stats["total_processed"] == 1000
        assert stats["errors"] == 0

        # Calculate throughput
        throughput = stats["inserted"] / duration
        print(f"\n📊 Medium Dataset Performance:")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Throughput: {throughput:.2f} items/sec")
        print(f"   Memory usage: {memory_delta:.2f}MB")

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_batch_size_optimization(self, db_session: AsyncSession):
        """Test different batch sizes to find optimal configuration."""
        service = HuggingFaceIngestionService()
        mock_data = generate_mock_dataset(500)
        user_id = "perf-test-user"

        batch_sizes = [10, 25, 50, 100, 200]
        results = {}

        for batch_size in batch_sizes:
            start_time = time.time()

            with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock:
                mock.return_value = mock_data

                stats = await service.ingest_from_dataset(
                    db=db_session,
                    dataset_name=f"perf-test-{batch_size}",
                    max_samples=500,
                    user_id=user_id,
                    batch_size=batch_size,
                )

            duration = time.time() - start_time
            throughput = stats["inserted"] / duration

            results[batch_size] = {
                "duration": duration,
                "throughput": throughput,
                "memory": get_memory_usage(),
            }

        # Print optimization results
        print("\n📊 Batch Size Optimization Results:")
        for batch_size, metrics in results.items():
            print(
                f"   Batch {batch_size:3d}: {metrics['duration']:.2f}s, "
                f"{metrics['throughput']:.2f} items/sec, "
                f"{metrics['memory']:.2f}MB"
            )

        # Verify all completed successfully
        assert all(r["throughput"] > 0 for r in results.values())

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_memory_usage_large_dataset(self, db_session: AsyncSession):
        """Test memory usage with large dataset."""
        service = HuggingFaceIngestionService()
        dataset_size = 5000
        mock_data = generate_mock_dataset(dataset_size)
        user_id = "perf-test-user"

        memory_samples = []
        start_memory = get_memory_usage()

        async def memory_monitor():
            while True:
                memory_samples.append(get_memory_usage())
                await asyncio.sleep(1)

        # Start memory monitoring
        monitor_task = asyncio.create_task(memory_monitor())

        try:
            with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock:
                mock.return_value = mock_data

                stats = await service.ingest_from_dataset(
                    db=db_session,
                    dataset_name="perf-test-large",
                    max_samples=dataset_size,
                    user_id=user_id,
                    batch_size=100,
                )
        finally:
            monitor_task.cancel()

        end_memory = get_memory_usage()
        peak_memory = max(memory_samples) if memory_samples else end_memory
        memory_delta = peak_memory - start_memory

        print(f"\n📊 Large Dataset Memory Usage:")
        print(f"   Dataset size: {dataset_size} items")
        print(f"   Start memory: {start_memory:.2f}MB")
        print(f"   Peak memory: {peak_memory:.2f}MB")
        print(f"   Memory delta: {memory_delta:.2f}MB")
        print(f"   Per-item memory: {memory_delta/dataset_size*1024:.2f}KB")

        # Memory usage should be reasonable
        assert memory_delta < 1000  # Less than 1GB increase
        assert stats["total_processed"] == dataset_size

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_parallel_processing(self, db_session: AsyncSession):
        """Test parallel processing performance."""

        async def process_batch(batch_id: int, size: int):
            service = HuggingFaceIngestionService()
            mock_data = generate_mock_dataset(size)

            with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock:
                mock.return_value = mock_data

                return await service.ingest_from_dataset(
                    db=db_session,
                    dataset_name=f"parallel-{batch_id}",
                    max_samples=size,
                    user_id=f"user-{batch_id}",
                    batch_size=25,
                )

        # Test sequential vs parallel
        batch_size = 200
        num_batches = 4

        # Sequential processing
        start_sequential = time.time()
        sequential_results = []
        for i in range(num_batches):
            result = await process_batch(i, batch_size)
            sequential_results.append(result)
        sequential_duration = time.time() - start_sequential

        # Parallel processing
        start_parallel = time.time()
        parallel_results = await asyncio.gather(
            *[process_batch(i + num_batches, batch_size) for i in range(num_batches)]
        )
        parallel_duration = time.time() - start_parallel

        speedup = sequential_duration / parallel_duration

        print(f"\n📊 Parallel Processing Performance:")
        print(f"   Sequential: {sequential_duration:.2f}s")
        print(f"   Parallel: {parallel_duration:.2f}s")
        print(f"   Speedup: {speedup:.2f}x")

        # Parallel should be faster or at least not significantly slower
        assert parallel_duration <= sequential_duration * 1.5
        assert len(parallel_results) == num_batches

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_vector_store_population_speed(self, db_session: AsyncSession):
        """Benchmark vector store population speed."""
        # Pre-populate database with lyrics
        for i in range(100):
            lyrics = Lyrics(
                id=i + 1,
                title=f"Vector Test {i}",
                content=f"Content for vector testing {i}" * 20,
                genre="pop",
                user_id="vector-test-user",
            )
            db_session.add(lyrics)
        await db_session.commit()

        service = ChromaDBPopulationService()
        start_time = time.time()
        start_memory = get_memory_usage()

        with patch.object(service, "vector_store") as mock_store:
            mock_store.add_documents = MagicMock(return_value=True)
            mock_store.count = MagicMock(return_value=0)

            stats = await service.populate_from_database(
                db=db_session, batch_size=32, chunk_size=512
            )

        duration = time.time() - start_time
        memory_delta = get_memory_usage() - start_memory

        throughput = stats["documents_indexed"] / duration

        print(f"\n📊 Vector Store Population Performance:")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Throughput: {throughput:.2f} docs/sec")
        print(f"   Memory usage: {memory_delta:.2f}MB")

        assert duration < 30  # Should complete in under 30 seconds
        assert stats["documents_indexed"] > 0

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_chunking_performance(self):
        """Benchmark text chunking performance."""
        service = ChromaDBPopulationService()

        # Generate large text
        large_text = "Line of text\n" * 10000  # ~130KB

        chunk_configs = [
            (256, 25),
            (512, 50),
            (1024, 100),
        ]

        results = {}

        for chunk_size, overlap in chunk_configs:
            start_time = time.time()

            chunks = service._chunk_text(large_text, chunk_size=chunk_size, overlap=overlap)

            duration = time.time() - start_time

            results[(chunk_size, overlap)] = {
                "duration": duration,
                "num_chunks": len(chunks),
                "throughput": len(large_text) / duration,
            }

        print(f"\n📊 Chunking Performance:")
        for config, metrics in results.items():
            chunk_size, overlap = config
            print(
                f"   {chunk_size}/{overlap}: {metrics['duration']:.4f}s, "
                f"{metrics['num_chunks']} chunks, "
                f"{metrics['throughput']:.0f} chars/sec"
            )

        # All configurations should be fast
        assert all(r["duration"] < 1.0 for r in results.values())

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_database_query_performance(self, db_session: AsyncSession):
        """Benchmark database query performance."""
        # Pre-populate with many lyrics
        for i in range(1000):
            lyrics = Lyrics(
                id=i + 1,
                title=f"Query Test {i}",
                content=f"Content {i}" * 10,
                genre=["pop", "rock", "hip-hop"][i % 3],
                user_id="query-test-user",
            )
            db_session.add(lyrics)
        await db_session.commit()

        # Test different query patterns
        from sqlalchemy import func, select

        queries = {
            "simple_select": select(Lyrics).limit(100),
            "filtered": select(Lyrics).where(Lyrics.genre == "pop").limit(100),
            "count": select(func.count(Lyrics.id)),
            "ordered": select(Lyrics).order_by(Lyrics.created_at.desc()).limit(100),
        }

        results = {}

        for query_name, query in queries.items():
            start_time = time.time()

            for _ in range(10):  # Run 10 times
                await db_session.execute(query)

            duration = time.time() - start_time
            avg_time = duration / 10

            results[query_name] = {"avg_time": avg_time, "qps": 1 / avg_time}

        print(f"\n📊 Database Query Performance:")
        for query_name, metrics in results.items():
            print(
                f"   {query_name:15s}: {metrics['avg_time']*1000:.2f}ms, "
                f"{metrics['qps']:.0f} QPS"
            )

        # Queries should be fast
        assert all(r["avg_time"] < 0.1 for r in results.values())


@pytest.mark.asyncio
async def test_end_to_end_performance(db_session: AsyncSession):
    """End-to-end performance test of complete ingestion pipeline."""
    print(f"\n{'='*60}")
    print(f"🚀 END-TO-END PERFORMANCE TEST")
    print(f"{'='*60}")

    overall_start = time.time()
    start_memory = get_memory_usage()

    # Phase 1: Ingestion
    print(f"\n📥 Phase 1: Data Ingestion")
    ingestion_service = HuggingFaceIngestionService()
    mock_data = generate_mock_dataset(1000)

    phase1_start = time.time()
    with patch("app.services.ingestion.huggingface_ingestion.load_dataset") as mock:
        mock.return_value = mock_data

        ingestion_stats = await ingestion_service.ingest_from_dataset(
            db=db_session,
            dataset_name="e2e-perf-test",
            max_samples=1000,
            user_id="e2e-test-user",
            batch_size=50,
        )
    phase1_duration = time.time() - phase1_start

    print(f"   ✓ Ingested {ingestion_stats['inserted']} items")
    print(f"   ✓ Duration: {phase1_duration:.2f}s")
    print(f"   ✓ Throughput: {ingestion_stats['inserted']/phase1_duration:.2f} items/sec")

    # Phase 2: Vector Store Population
    print(f"\n🔍 Phase 2: Vector Store Population")
    population_service = ChromaDBPopulationService()

    phase2_start = time.time()
    with patch.object(population_service, "vector_store") as mock_store:
        mock_store.add_documents = MagicMock(return_value=True)
        mock_store.count = MagicMock(return_value=0)

        population_stats = await population_service.populate_from_database(
            db=db_session, batch_size=32, chunk_size=512
        )
    phase2_duration = time.time() - phase2_start

    print(f"   ✓ Indexed {population_stats['documents_indexed']} documents")
    print(f"   ✓ Duration: {phase2_duration:.2f}s")
    print(f"   ✓ Throughput: {population_stats['documents_indexed']/phase2_duration:.2f} docs/sec")

    # Overall metrics
    overall_duration = time.time() - overall_start
    end_memory = get_memory_usage()
    memory_delta = end_memory - start_memory

    print(f"\n📊 Overall Performance:")
    print(f"   Total duration: {overall_duration:.2f}s")
    print(f"   Memory usage: {memory_delta:.2f}MB")
    print(f"   Peak memory: {end_memory:.2f}MB")

    # Performance targets
    assert overall_duration < 120  # Complete in under 2 minutes
    assert memory_delta < 1000  # Use less than 1GB
    assert ingestion_stats["errors"] == 0
    assert population_stats["errors"] == 0

    print(f"\n✅ END-TO-END PERFORMANCE TEST PASSED")
    print(f"{'='*60}\n")
