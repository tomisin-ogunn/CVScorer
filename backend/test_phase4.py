"""
Phase 4 Test Suite: Token & Cost Optimizations
Tests caching, usage tracking, and text optimization features.
"""

import sys
import os
import time
import logging

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from deterministic_matcher import (
    compute_similarity,
    compute_similarity_with_sections,
    get_phase4_stats,
    clear_cache,
    batch_compute_embeddings
)
from embedding_cache import get_cache
from usage_tracker import get_tracker
from text_optimizer import (
    optimize_text_for_embedding,
    truncate_text,
    count_tokens,
    calculate_token_savings
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_cache():
    """Test that embeddings are cached properly."""
    print("\n" + "=" * 70)
    print("TEST 1: Embedding Cache")
    print("=" * 70)
    
    cache = get_cache()
    
    # Clear cache before testing
    print("Clearing cache...")
    cache.clear()
    
    test_text = "Python developer with 5 years of experience"
    
    # First call - should be a cache miss
    print("\n1. First embedding call (should miss cache)...")
    start = time.time()
    result1 = compute_similarity(test_text, "Looking for Python developer")
    time1 = time.time() - start
    
    stats1 = cache.get_stats()
    print(f"   Time: {time1:.3f}s")
    print(f"   Cache stats: {stats1}")
    
    # Second call with same text - should be a cache hit
    print("\n2. Second embedding call (should hit cache)...")
    start = time.time()
    result2 = compute_similarity(test_text, "Looking for Python developer")
    time2 = time.time() - start
    
    stats2 = cache.get_stats()
    print(f"   Time: {time2:.3f}s")
    print(f"   Cache stats: {stats2}")
    print(f"   Speed improvement: {time1/time2:.1f}x faster")
    
    # Verify results are the same
    assert abs(result1['similarity_score'] - result2['similarity_score']) < 0.01, \
        "Cached result should be identical"
    
    print("\n✓ Cache test passed!")
    print(f"  - Cache hit rate: {stats2['hit_rate_percent']}%")
    print(f"  - Total requests: {stats2['total_requests']}")
    

def test_usage_tracking():
    """Test usage tracking functionality."""
    print("\n" + "=" * 70)
    print("TEST 2: Usage Tracking")
    print("=" * 70)
    
    tracker = get_tracker()
    
    # Get initial stats
    initial_stats = tracker.get_usage_summary()
    print(f"\nInitial stats:")
    print(f"  Total requests: {initial_stats['total']['requests']}")
    print(f"  Total tokens: {initial_stats['total']['tokens']}")
    print(f"  Cached requests: {initial_stats['total']['cached_requests']}")
    
    # Make a request
    test_cv = "Software engineer with React and Node.js experience"
    test_job = "Looking for React developer"
    
    print("\nMaking a test request...")
    compute_similarity(test_cv, test_job)
    
    # Get updated stats
    updated_stats = tracker.get_usage_summary()
    print(f"\nUpdated stats:")
    print(f"  Total requests: {updated_stats['total']['requests']}")
    print(f"  Total tokens: {updated_stats['total']['tokens']}")
    print(f"  Cached requests: {updated_stats['total']['cached_requests']}")
    print(f"  Cache hit rate: {updated_stats['total']['cache_hit_rate_percent']}%")
    
    # Check rate limits
    rate_limit_status = tracker.check_rate_limits('gemini-embedding-001')
    print(f"\nRate limit status:")
    print(f"  {rate_limit_status['message']}")
    print(f"  Within limits: {rate_limit_status['within_limits']}")
    
    print("\n✓ Usage tracking test passed!")


def test_text_optimization():
    """Test text optimization features."""
    print("\n" + "=" * 70)
    print("TEST 3: Text Optimization")
    print("=" * 70)
    
    # Test with long text
    long_text = """
    Senior Software Engineer Position
    
    We are seeking a highly skilled and experienced Senior Software Engineer to join our dynamic team.
    This is an excellent opportunity for someone who is passionate about technology and wants to make
    a significant impact on our products.
    
    Requirements:
    - 5+ years of professional software development experience
    - Strong proficiency in Python, JavaScript, and TypeScript
    - Experience with modern web frameworks like React, Angular, or Vue.js
    - Backend development experience with Node.js, Django, or Flask
    - Database expertise with PostgreSQL, MongoDB, or MySQL
    - Experience with Docker and Kubernetes
    - Knowledge of AWS, Azure, or GCP cloud platforms
    - Excellent problem-solving and communication skills
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable, and well-documented code
    - Participate in code reviews and mentor junior developers
    - Contribute to architectural decisions
    - Stay up-to-date with emerging technologies
    
    We are an equal opportunity employer and welcome applications from all qualified candidates.
    Please send your resume and cover letter to careers@example.com
    
    Copyright 2024 Example Corp. All rights reserved. This job posting is confidential
    and not to be shared without permission.
    """ * 3  # Make it longer
    
    print(f"\nOriginal text:")
    print(f"  Characters: {len(long_text)}")
    print(f"  Estimated tokens: {count_tokens(long_text)}")
    
    # Optimize text
    optimized = optimize_text_for_embedding(long_text, max_tokens=500)
    
    print(f"\nOptimized text:")
    print(f"  Characters: {len(optimized)}")
    print(f"  Estimated tokens: {count_tokens(optimized)}")
    
    # Calculate savings
    savings = calculate_token_savings(long_text, optimized)
    print(f"\nToken savings:")
    print(f"  Tokens saved: {savings['tokens_saved']}")
    print(f"  Savings: {savings['savings_percent']}%")
    
    assert savings['tokens_saved'] > 0, "Should save tokens"
    
    print("\n✓ Text optimization test passed!")


def test_batch_processing():
    """Test batch embedding processing."""
    print("\n" + "=" * 70)
    print("TEST 4: Batch Processing")
    print("=" * 70)
    
    # Create multiple CVs
    cvs = [
        "Python developer with 3 years of experience",
        "React specialist with frontend expertise",
        "Full-stack engineer with Node.js and PostgreSQL",
        "DevOps engineer with Docker and Kubernetes",
        "Data scientist with machine learning experience"
    ]
    
    print(f"\nBatch processing {len(cvs)} texts...")
    
    start = time.time()
    embeddings = batch_compute_embeddings(cvs, use_cache=True)
    elapsed = time.time() - start
    
    print(f"\nCompleted in {elapsed:.2f}s")
    print(f"Average time per embedding: {elapsed/len(cvs):.2f}s")
    print(f"Generated {len(embeddings)} embeddings")
    
    # Verify all embeddings were generated
    assert len(embeddings) == len(cvs), "Should generate all embeddings"
    
    # Run again to test cache effectiveness
    print("\n\nRunning batch again (should be faster with cache)...")
    start = time.time()
    embeddings2 = batch_compute_embeddings(cvs, use_cache=True)
    elapsed2 = time.time() - start
    
    print(f"Completed in {elapsed2:.2f}s")
    print(f"Speed improvement: {elapsed/elapsed2:.1f}x faster")
    
    print("\n✓ Batch processing test passed!")


def test_phase4_integration():
    """Test Phase 4 integration with existing phases."""
    print("\n" + "=" * 70)
    print("TEST 5: Phase 4 Integration with Phase 1+2+3")
    print("=" * 70)
    
    test_cv = """
    John Doe
    Senior Software Engineer
    
    Skills:
    Python, JavaScript, React, Node.js, PostgreSQL, Docker, Kubernetes, AWS
    
    Experience:
    Software Engineer at Tech Corp (2019-2024)
    - Built scalable web applications
    - Implemented microservices architecture
    
    Education:
    BS Computer Science, MIT (2015-2019)
    """
    
    test_job = """
    Senior Software Engineer
    
    Skills:
    Python, React, Node.js, PostgreSQL, Docker, AWS
    
    Experience:
    5+ years of software development
    
    Education:
    BS in Computer Science
    """
    
    # Test Phase 1+2 with Phase 4 optimizations
    print("\n1. Testing Phase 1+2 with Phase 4...")
    result = compute_similarity(test_cv, test_job)
    print(f"   Similarity score: {result['similarity_score']}%")
    print(f"   Matched keywords: {len(result['matched_keywords'])}")
    
    # Test Phase 3 with Phase 4 optimizations
    print("\n2. Testing Phase 3 with Phase 4...")
    result_sections = compute_similarity_with_sections(test_cv, test_job)
    print(f"   Overall similarity: {result_sections['overall_similarity']}%")
    print(f"   Section scores: {result_sections['sections']}")
    
    # Get Phase 4 stats
    print("\n3. Phase 4 Statistics:")
    stats = get_phase4_stats()
    print(f"   Cache hit rate: {stats['cache']['hit_rate_percent']}%")
    print(f"   Cache files: {stats['cache_size']['file_count']}")
    print(f"   Total API requests: {stats['usage']['total']['requests']}")
    print(f"   Cached requests: {stats['usage']['total']['cached_requests']}")
    
    print("\n✓ Phase 4 integration test passed!")


def test_truncation():
    """Test text truncation functionality."""
    print("\n" + "=" * 70)
    print("TEST 6: Text Truncation")
    print("=" * 70)
    
    long_text = "This is a test sentence. " * 200  # Very long text
    
    print(f"\nOriginal text:")
    print(f"  Estimated tokens: {count_tokens(long_text)}")
    
    # Truncate to 100 tokens
    truncated = truncate_text(long_text, max_tokens=100)
    
    print(f"\nTruncated text:")
    print(f"  Estimated tokens: {count_tokens(truncated)}")
    
    assert count_tokens(truncated) <= 110, "Should truncate to approximately target"
    
    print("\n✓ Truncation test passed!")


def run_all_tests():
    """Run all Phase 4 tests."""
    print("\n" + "=" * 70)
    print("PHASE 4: TOKEN & COST OPTIMIZATION TEST SUITE")
    print("=" * 70)
    
    try:
        test_embedding_cache()
        test_usage_tracking()
        test_text_optimization()
        test_batch_processing()
        test_truncation()
        test_phase4_integration()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)
        
        # Print final statistics
        print("\n\nFinal Phase 4 Statistics:")
        print("-" * 70)
        stats = get_phase4_stats()
        
        print("\nCache Statistics:")
        print(f"  Hit rate: {stats['cache']['hit_rate_percent']}%")
        print(f"  Hits: {stats['cache']['hits']}")
        print(f"  Misses: {stats['cache']['misses']}")
        print(f"  Cache size: {stats['cache_size']['file_count']} files ({stats['cache_size']['total_mb']} MB)")
        
        print("\nUsage Statistics:")
        print(f"  Total API requests: {stats['usage']['total']['requests']}")
        print(f"  Cached requests: {stats['usage']['total']['cached_requests']}")
        print(f"  Total tokens: {stats['usage']['total']['tokens']}")
        print(f"  Total cost: ${stats['usage']['total']['cost']:.4f}")
        
        # Calculate token savings from caching
        cache_hits = stats['cache']['hits']
        avg_tokens_per_request = 500  # Conservative estimate
        tokens_saved = cache_hits * avg_tokens_per_request
        print(f"\nEstimated token savings from caching: ~{tokens_saved} tokens")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
