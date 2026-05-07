"""
Comprehensive test suite for CV scoring system
"""
import sys
import logging
from deterministic_matcher import compute_similarity

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce log noise
logger = logging.getLogger(__name__)

def run_test(name, cv, job, expected_min, expected_max):
    """Helper function to run a test case"""
    print(f"\nTesting: {name}")
    result = compute_similarity(cv, job)
    score = result['similarity_score']
    
    passed = expected_min <= score <= expected_max
    status = "PASS" if passed else "FAIL"
    
    print(f"  Score: {score}% (Expected: {expected_min}-{expected_max}%)")
    print(f"  Matched: {len(result['matched_keywords'])} keywords")
    print(f"  Missing: {len(result['missing_keywords'])} keywords")
    print(f"  Status: {status}")
    
    return passed, score

def main():
    print("="*80)
    print("COMPREHENSIVE CV SCORING TEST SUITE")
    print("="*80)
    
    tests = []
    
    # Test 1: Random words should score very low
    print("\n" + "-"*80)
    print("Category: Random/Garbage Input")
    print("-"*80)
    
    passed, score = run_test(
        "Random words vs CV",
        cv="""John Doe, Senior Software Engineer with Python, React, AWS, 5 years experience""",
        job="banana elephant purple bicycle mountain sunshine rainbow",
        expected_min=0,
        expected_max=30
    )
    tests.append(("Random words", passed, score, "0-30"))
    
    passed, score = run_test(
        "Short random text vs Job",
        cv="hello world test foo bar baz",
        job="""Senior Software Engineer - Python, React, Node.js, AWS, 5+ years experience required""",
        expected_min=0,
        expected_max=30
    )
    tests.append(("Short random", passed, score, "0-30"))
    
    # Test 2: Perfect matches should score high
    print("\n" + "-"*80)
    print("Category: Perfect/Excellent Matches")
    print("-"*80)
    
    passed, score = run_test(
        "Perfect match - All requirements met",
        cv="""
        John Doe - Senior Software Engineer
        Skills: Python (5 years), JavaScript, React, Node.js, PostgreSQL, AWS, Docker, Kubernetes, CI/CD
        Experience: Built microservices, led development teams, 5+ years
        Education: BS Computer Science
        """,
        job="""
        Senior Software Engineer
        Requirements: Python, React, Node.js, PostgreSQL, AWS, Docker, Kubernetes, CI/CD
        5+ years experience, BS Computer Science
        """,
        expected_min=70,
        expected_max=100
    )
    tests.append(("Perfect match", passed, score, "70-100"))
    
    # Test 3: Good matches (partial requirements)
    print("\n" + "-"*80)
    print("Category: Good Matches (Partial Requirements)")
    print("-"*80)
    
    passed, score = run_test(
        "Good match - Most requirements met",
        cv="""
        Jane Smith - Software Engineer
        Skills: Python (3 years), React, JavaScript, PostgreSQL, Docker
        Experience: Web development, REST APIs, 3 years
        Education: BS Computer Science
        """,
        job="""
        Senior Software Engineer
        Requirements: Python (5+ years), React, Node.js, PostgreSQL, AWS, Docker, Kubernetes
        """,
        expected_min=50,
        expected_max=75
    )
    tests.append(("Good match", passed, score, "50-75"))
    
    # Test 4: Poor matches (wrong field)
    print("\n" + "-"*80)
    print("Category: Poor Matches (Wrong Field/Unrelated)")
    print("-"*80)
    
    passed, score = run_test(
        "Wrong field - Marketing vs Engineering",
        cv="""
        Sarah Johnson - Marketing Manager
        Skills: Social Media, SEO, Google Analytics, Content Strategy, Email Marketing
        Experience: Marketing campaigns, brand awareness, 5 years
        Education: BA Marketing
        """,
        job="""
        Senior Software Engineer
        Requirements: Python, React, Node.js, PostgreSQL, AWS, 5+ years programming
        """,
        expected_min=0,
        expected_max=35
    )
    tests.append(("Wrong field", passed, score, "0-35"))
    
    passed, score = run_test(
        "Wrong field - Accountant vs Engineering",
        cv="""
        Michael Brown - Senior Accountant
        Skills: QuickBooks, Excel, Financial Analysis, Tax Preparation
        Experience: Financial reporting, audits, 7 years
        Education: BA Accounting, CPA
        """,
        job="""
        Software Engineer - Python, Django, React, PostgreSQL, AWS
        """,
        expected_min=0,
        expected_max=35
    )
    tests.append(("Accountant vs Dev", passed, score, "0-35"))
    
    # Test 5: Moderate matches (related but junior)
    print("\n" + "-"*80)
    print("Category: Moderate Matches (Junior/Entry-level)")
    print("-"*80)
    
    passed, score = run_test(
        "Junior candidate for senior role",
        cv="""
        Alex Kim - Junior Developer
        Skills: Python (1 year), JavaScript, HTML, CSS, Git
        Experience: Built small web apps, internship, 1 year
        Education: BS Computer Science (Recent Graduate)
        """,
        job="""
        Senior Software Engineer
        Requirements: Python (5+ years), React, Node.js, PostgreSQL, AWS, team leadership
        """,
        expected_min=30,
        expected_max=55
    )
    tests.append(("Junior for Senior", passed, score, "30-55"))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total = len(tests)
    passed_count = sum(1 for _, passed, _, _ in tests if passed)
    
    print(f"\nResults: {passed_count}/{total} tests passed\n")
    
    for name, passed, score, expected in tests:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name:25s} {score:5.1f}% (expected: {expected})")
    
    if passed_count == total:
        print("\n" + "="*80)
        print("ALL TESTS PASSED - Scoring system working correctly!")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print(f"SOME TESTS FAILED - {total - passed_count} test(s) need attention")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
