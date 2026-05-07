"""
Phase 1, 2, 3 & 4: Deterministic CV Matching using Gemini Embeddings
Phase 1: Uses cosine similarity on embeddings for stable, reproducible results.
Phase 2: Extracts keywords/skills from job description and checks against CV.
Phase 3: Section-based similarity for granular analysis of skills, experience, and education.
Phase 4: Token & Cost Optimizations - caching, text optimization, usage tracking.
"""

import os
import re
import logging
from typing import Dict, List, Set, Optional
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

# Phase 4: Import optimization modules
from embedding_cache import get_cache
from usage_tracker import get_tracker
from text_optimizer import (
    optimize_text_for_embedding,
    truncate_text,
    count_tokens
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Phase 4: Initialize cache and tracker
_embedding_cache = get_cache()
_usage_tracker = get_tracker()


def preprocess_text(text: str) -> str:
    """
    Preprocess text for deterministic embedding generation.
    
    Steps:
    1. Convert to lowercase
    2. Remove extra whitespace
    3. Trim leading/trailing whitespace
    4. Optional: Remove punctuation (keeping it for now as it may carry semantic meaning)
    
    Args:
        text: Input text to preprocess
        
    Returns:
        Preprocessed text
    """
    # Convert to lowercase for consistency
    text = text.lower()
    
    # Remove extra whitespace (multiple spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def get_embedding(text: str, use_cache: bool = True, optimize: bool = True) -> np.ndarray:
    """
    Get embedding vector from Gemini Embeddings API.
    
    Phase 4: Now supports caching and text optimization.
    
    Args:
        text: Text to embed
        use_cache: If True, check cache before making API call (Phase 4)
        optimize: If True, optimize text before embedding (Phase 4)
        
    Returns:
        NumPy array containing the embedding vector
    """
    model_name = "gemini-embedding-001"
    
    try:
        # Phase 4: Optimize text to reduce tokens
        original_text = text
        if optimize:
            text = optimize_text_for_embedding(text, max_tokens=2000)
        
        # Phase 4: Check cache first
        if use_cache:
            cached_embedding = _embedding_cache.get(text, model_name)
            if cached_embedding is not None:
                logger.info(f"Using cached embedding (dimension: {len(cached_embedding)})")
                _usage_tracker.track_request(
                    model=model_name,
                    text_length=len(text),
                    tokens=count_tokens(text),
                    cached=True
                )
                return cached_embedding
        
        # Phase 4: Make API call and track usage
        logger.info(f"Generating new embedding (text length: {len(text)} chars, ~{count_tokens(text)} tokens)")
        
        result = genai.embed_content(
            model=f"models/{model_name}",
            content=text,
            task_type="retrieval_document"
        )
        
        # Convert to numpy array for mathematical operations
        embedding = np.array(result['embedding'])
        
        logger.info(f"Generated embedding with dimension: {len(embedding)}")
        
        # Phase 4: Cache the result
        if use_cache:
            _embedding_cache.put(text, embedding, model_name)
        
        # Phase 4: Track usage
        _usage_tracker.track_request(
            model=model_name,
            text_length=len(text),
            tokens=count_tokens(text),
            cached=False
        )
        
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise Exception(f"Embedding generation failed: {str(e)}")


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Cosine similarity = (A · B) / (||A|| * ||B||)
    
    This is deterministic vector math - given the same inputs,
    it will always produce the same output.
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
        
    Returns:
        Cosine similarity score between -1 and 1 (typically 0 to 1 for similar content)
    """
    # Calculate dot product
    dot_product = np.dot(vec1, vec2)
    
    # Calculate magnitudes (L2 norms)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Calculate cosine similarity
    similarity = dot_product / (norm1 * norm2)
    
    return float(similarity)


def extract_keywords_from_text(text: str) -> Set[str]:
    """
    Extract potential keywords/skills from text using rule-based approach.
    
    This improved extraction focuses on:
    1. Known technical skills and technologies
    2. Multi-word technical phrases (e.g., "machine learning", "cloud computing")
    3. Technical acronyms and abbreviations
    4. Filtering out generic business/HR jargon
    
    Args:
        text: Text to extract keywords from
        
    Returns:
        Set of extracted keywords (lowercase for matching)
    """
    # Comprehensive tech skills database with synonyms
    KNOWN_SKILLS = {
        # Programming languages
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
        'go', 'rust', 'typescript', 'sql', 'r', 'matlab', 'scala', 'perl', 'shell',
        'bash', 'powershell', 'c', 'objective-c', 'dart', 'elixir', 'haskell', 'lua',
        'groovy', 'vb.net', 'visual basic', 'fortran', 'cobol', 'assembly',
        
        # Web frameworks & libraries
        'react', 'angular', 'vue', 'vue.js', 'node.js', 'nodejs', 'express', 'express.js',
        'django', 'flask', 'spring', 'spring boot', 'asp.net', 'rails', 'ruby on rails',
        'laravel', 'jquery', 'bootstrap', 'tailwind', 'tailwind css', 'next.js', 'nextjs',
        'nuxt', 'nuxt.js', 'svelte', 'ember', 'ember.js', 'backbone', 'backbone.js',
        'fastapi', 'nest.js', 'nestjs', 'meteor', 'gatsby', 'redux', 'mobx', 'rxjs',
        
        # Databases
        'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'elasticsearch',
        'oracle', 'sql server', 'mssql', 'sqlite', 'dynamodb', 'cassandra', 'neo4j',
        'mariadb', 'couchdb', 'firebase', 'firestore', 'realm', 'snowflake',
        'bigquery', 'redshift', 'aurora', 'cosmosdb', 'memcached', 'influxdb',
        'nosql',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
        'jenkins', 'gitlab', 'github', 'github actions', 'terraform', 'ansible',
        'ci/cd', 'circleci', 'travis', 'travis ci', 'bitbucket', 'chef', 'puppet',
        'vagrant', 'helm', 'istio', 'prometheus', 'grafana', 'datadog', 'new relic',
        'cloudformation', 'lambda', 'ec2', 's3', 'cloudfront', 'route 53',
        
        # Tools & Technologies
        'git', 'svn', 'mercurial', 'linux', 'unix', 'windows', 'macos', 'ubuntu',
        'centos', 'debian', 'rest', 'rest api', 'restful', 'graphql', 'grpc',
        'soap', 'api', 'microservices', 'agile', 'scrum', 'kanban', 'jira',
        'confluence', 'slack', 'teams', 'trello', 'asana', 'notion',
        'websockets', 'oauth', 'jwt', 'saml', 'ldap', 'active directory',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'artificial intelligence', 'ai',
        'ml', 'nlp', 'natural language processing', 'computer vision', 'cv',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas',
        'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'jupyter',
        'data analysis', 'data science', 'statistics', 'neural networks',
        'cnn', 'rnn', 'lstm', 'transformers', 'bert', 'gpt', 'llm',
        
        # Mobile
        'ios', 'android', 'react native', 'flutter', 'xamarin', 'ionic',
        'cordova', 'phonegap', 'swift ui', 'swiftui', 'jetpack compose',
        
        # Testing & Quality
        'jest', 'mocha', 'chai', 'pytest', 'unittest', 'junit', 'testng',
        'selenium', 'cypress', 'playwright', 'puppeteer', 'webdriver',
        'test automation', 'unit testing', 'integration testing', 'e2e',
        'tdd', 'bdd', 'quality assurance', 'qa',
        
        # Frontend & Styling
        'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'stylus',
        'webpack', 'vite', 'rollup', 'parcel', 'babel', 'npm', 'yarn',
        'pnpm', 'responsive design', 'ui/ux', 'figma', 'sketch', 'adobe xd',
        
        # Backend & Architecture
        'maven', 'gradle', 'microservices', 'monolith', 'serverless',
        'event-driven', 'message queue', 'rabbitmq', 'kafka', 'activemq',
        'rest', 'soap', 'grpc', 'load balancing', 'caching', 'cdn',
        
        # Methodologies & Concepts
        'oop', 'object-oriented', 'functional programming', 'design patterns',
        'solid', 'clean code', 'code review', 'pair programming',
        'continuous integration', 'continuous deployment', 'devops',
        'site reliability engineering', 'sre', 'distributed systems',
        
        # Security
        'security', 'penetration testing', 'owasp', 'encryption', 'ssl', 'tls',
        'vulnerability assessment', 'firewall', 'vpn', 'authentication',
        'authorization', 'security best practices',
        
        # Business Intelligence & Analytics
        'tableau', 'power bi', 'looker', 'qlik', 'metabase', 'superset',
        'data warehouse', 'etl', 'data pipeline', 'spark', 'hadoop', 'hive',
        'presto', 'airflow', 'dbt'
    }
    
    # Multi-word technical phrases to look for specifically
    MULTI_WORD_SKILLS = {
        'machine learning', 'deep learning', 'natural language processing',
        'computer vision', 'data analysis', 'data science', 'artificial intelligence',
        'continuous integration', 'continuous deployment', 'test automation',
        'unit testing', 'integration testing', 'load balancing', 'message queue',
        'distributed systems', 'design patterns', 'functional programming',
        'object-oriented programming', 'site reliability engineering',
        'penetration testing', 'vulnerability assessment', 'data warehouse',
        'rest api', 'graphql api', 'web services', 'cloud computing',
        'responsive design', 'mobile development', 'full stack', 'front end',
        'back end', 'version control', 'code review', 'agile methodology',
        'scrum master', 'product owner', 'software development',
        'software engineering', 'database design', 'system architecture',
        'api design', 'user experience', 'user interface'
    }
    
    # Expanded exclusion list for generic HR/business terms
    EXCLUDED_WORDS = {
        # Job titles and levels
        'experience', 'experienced', 'knowledge', 'skills', 'requirements', 
        'preferred', 'required', 'bs', 'ba', 'ms', 'mba', 'phd', 'degree', 
        'education', 'work', 'years', 'year', 'senior', 'junior', 'mid',
        'engineer', 'developer', 'designer', 'manager', 'lead', 'architect',
        'director', 'principal', 'staff', 'intern', 'entry', 'level',
        
        # Generic descriptors
        'related', 'field', 'strong', 'excellent', 'good', 'great', 'must',
        'should', 'could', 'would', 'can', 'able', 'ability', 'capable',
        'team', 'teams', 'project', 'projects', 'working', 'development', 'nice',
        'have', 'has', 'had', 'bonus', 'plus', 'position', 'role', 'job',
        'familiarity', 'familiar', 'proficiency', 'proficient',
        
        # Company/organizational terms
        'company', 'organization', 'department', 'looking', 'seeking',
        'want', 'need', 'needs', 'us', 'we', 'our', 'your', 'you',
        'candidate', 'candidates', 'hire', 'hiring', 'join', 'apply',
        
        # Time and location
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday', 'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        'remote', 'hybrid', 'onsite', 'location', 'office', 'home',
        
        # Common verbs and adjectives
        'understand', 'understanding', 'implement', 'build', 'create',
        'design', 'maintain', 'support', 'help', 'assist', 'collaborate',
        'communicate', 'collaborate', 'responsible', 'responsibilities',
        'provide', 'ensure', 'deliver', 'quality', 'high', 'low',
        'best', 'better', 'new', 'current', 'modern', 'latest',
        
        # Education terms
        'bachelor', 'master', 'doctorate', 'college', 'university',
        'school', 'graduate', 'undergraduate', 'certification', 'certified',
        
        # Common business words
        'business', 'client', 'customer', 'user', 'users', 'stakeholder',
        'stakeholders', 'product', 'service', 'solution', 'solutions',
        'platform', 'system', 'systems', 'application', 'applications',
        'process', 'processes', 'workflow', 'environment', 'production',
        
        # Generic tech buzzwords (too vague without context)
        'technology', 'technologies', 'software', 'hardware', 'tool',
        'tools', 'framework', 'frameworks', 'library', 'libraries',
        'code', 'coding', 'programming', 'scripting', 'full', 'stack',
        
        # Pronouns and common words
        'this', 'that', 'these', 'those', 'the', 'and', 'or', 'but',
        'with', 'from', 'for', 'about', 'between', 'through', 'during',
        'will', 'their', 'there', 'what', 'when', 'where', 'which',
        'who', 'how', 'why', 'other', 'others', 'such', 'some', 'any',
        'all', 'both', 'each', 'every', 'more', 'most', 'much', 'many',
        
        # Numbers and ranges
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'first', 'second', 'third',
        
        # Generic CV/resume words
        'summary', 'objective', 'profile', 'contact', 'references',
        'available', 'upon', 'request', 'name', 'email', 'phone', 'address',
        
        # Soft skills and buzzwords
        'innovative', 'dynamic', 'passionate', 'motivated', 'driven',
        'dedicated', 'enthusiastic', 'proactive', 'self-starter',
        'fast-paced', 'cutting-edge', 'state-of-the-art', 'world-class',
        'leading', 'premier', 'top-tier', 'competitive'
    }
    
    keywords = set()
    text_lower = text.lower()
    
    # Step 1: Extract multi-word skills first (more specific)
    for skill in MULTI_WORD_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            keywords.add(skill)
    
    # Step 2: Extract single-word known skills
    for skill in KNOWN_SKILLS:
        # Skip if already captured as part of multi-word skill
        if any(skill in mw for mw in keywords):
            continue
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            keywords.add(skill)
    
    # Step 3: Extract technical acronyms (2-6 uppercase letters)
    # But be more selective - must appear with tech context
    acronyms = re.findall(r'\b[A-Z]{2,6}\b', text)
    tech_context_words = {'sdk', 'ide', 'orm', 'mvc', 'mvvm', 'spa', 
                          'pwa', 'sso', 'cdn', 'dns', 'http', 'https', 'ssh',
                          'ftp', 'smtp', 'tcp', 'udp', 'lan', 'wan',
                          'vpn', 'ssl', 'tls', 'cors', 'csrf', 'xss', 'dos',
                          'ddos', 'crud', 'acid', 'base', 'cap', 'etl', 'elt',
                          'xml', 'json', 'yaml', 'csv', 'pdf', 'jwt', 'saml',
                          'ldap', 'smtp', 'imap', 'pop3'}
    
    for acronym in acronyms:
        acronym_lower = acronym.lower()
        # Only include if it's in our tech context list OR in known skills
        # But exclude standalone "ci" or "cd" - they should only appear as "ci/cd"
        if acronym_lower in ('ci', 'cd'):
            continue
        if acronym_lower in tech_context_words or acronym_lower in KNOWN_SKILLS:
            keywords.add(acronym_lower)
    
    # Step 4: Extract version numbers with technologies (e.g., "Python 3.9", "Java 11")
    # This helps identify specific technology requirements
    version_patterns = re.findall(
        r'\b([a-z]+\s*\d+(?:\.\d+)?)\b', 
        text_lower
    )
    for match in version_patterns:
        base_tech = re.sub(r'\s*\d+.*', '', match).strip()
        if base_tech in KNOWN_SKILLS:
            # Add both the base technology and the versioned form
            keywords.add(base_tech)
    
    # Step 5: Extract compound technical terms (e.g., "React.js", "Node.js", "ASP.NET")
    compound_terms = re.findall(
        r'\b[a-z]+\.[a-z]+\b|\b[a-z]+\-[a-z]+\b',
        text_lower
    )
    for term in compound_terms:
        # Only add if it's in our known skills list
        if term in KNOWN_SKILLS:
            keywords.add(term)
    
    # Step 6: Remove any accidentally captured excluded words
    keywords = {kw for kw in keywords if kw not in EXCLUDED_WORDS}
    
    # Step 7: Filter out overly generic single letters or very short terms
    # unless they're in our known skills list
    keywords = {
        kw for kw in keywords 
        if len(kw) > 2 or kw in KNOWN_SKILLS or kw in tech_context_words
    }
    
    # Step 8: Additional filter - remove words that are purely hyphened generic terms
    # unless they're in our known skills list
    generic_compound = {'cutting-edge', 'state-of-the-art', 'self-starter', 
                       'team-player', 'fast-paced', 'well-established'}
    keywords = {kw for kw in keywords if kw not in generic_compound}
    
    return keywords


def match_keywords(cv_text: str, job_keywords: Set[str]) -> tuple[List[str], List[str]]:
    """
    Check which keywords from the job description are present in the CV.
    
    Args:
        cv_text: The CV text to search in
        job_keywords: Set of keywords from the job description
        
    Returns:
        Tuple of (matched_keywords, missing_keywords)
    """
    cv_text_lower = cv_text.lower()
    matched = []
    missing = []
    
    for keyword in sorted(job_keywords):
        # Use word boundary matching for accurate results
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, cv_text_lower):
            matched.append(keyword)
        else:
            missing.append(keyword)
    
    return matched, missing


def detect_sections(text: str) -> Dict[str, str]:
    """
    Detect and extract major sections from CV or job description text.
    
    Looks for common section headers like:
    - Skills, Technical Skills, Core Competencies
    - Experience, Work Experience, Professional Experience, Employment History
    - Education, Academic Background
    
    Phase 3: Section-based similarity analysis
    
    Args:
        text: The CV or job description text
        
    Returns:
        Dictionary with keys: 'skills', 'experience', 'education', and 'other'
        Each value is the text content of that section.
    """
    # Initialize sections
    sections = {
        'skills': '',
        'experience': '',
        'education': '',
        'other': ''
    }
    
    # Normalize text for processing
    text_lines = text.split('\n')
    
    # Patterns for section headers (case-insensitive)
    skills_patterns = [
        r'^\s*skills?\s*:?\s*$',
        r'^\s*technical\s+skills?\s*:?\s*$',
        r'^\s*core\s+competenc(y|ies)\s*:?\s*$',
        r'^\s*technologies\s*:?\s*$',
        r'^\s*expertise\s*:?\s*$',
        r'^\s*proficienc(y|ies)\s*:?\s*$',
    ]
    
    experience_patterns = [
        r'^\s*(work\s+)?experience\s*:?\s*$',
        r'^\s*professional\s+experience\s*:?\s*$',
        r'^\s*employment\s+(history|background)\s*:?\s*$',
        r'^\s*work\s+history\s*:?\s*$',
        r'^\s*career\s+(history|summary)\s*:?\s*$',
        r'^\s*projects?\s*:?\s*$',
    ]
    
    education_patterns = [
        r'^\s*education\s*:?\s*$',
        r'^\s*academic\s+(background|qualifications?)\s*:?\s*$',
        r'^\s*qualifications?\s*:?\s*$',
        r'^\s*degrees?\s*:?\s*$',
        r'^\s*certifications?\s*:?\s*$',
    ]
    
    # Track which section we're currently in
    current_section = 'other'
    section_content = {key: [] for key in sections.keys()}
    
    for line in text_lines:
        line_lower = line.lower()
        
        # Check if this line is a section header
        is_header = False
        
        # Check skills headers
        for pattern in skills_patterns:
            if re.match(pattern, line_lower):
                current_section = 'skills'
                is_header = True
                break
        
        # Check experience headers
        if not is_header:
            for pattern in experience_patterns:
                if re.match(pattern, line_lower):
                    current_section = 'experience'
                    is_header = True
                    break
        
        # Check education headers
        if not is_header:
            for pattern in education_patterns:
                if re.match(pattern, line_lower):
                    current_section = 'education'
                    is_header = True
                    break
        
        # If it's not a header, add the line to the current section
        if not is_header:
            section_content[current_section].append(line)
    
    # Join lines back into text for each section
    for key in sections.keys():
        sections[key] = '\n'.join(section_content[key]).strip()
    
    # If we didn't detect any sections, put everything in 'other'
    # This handles unstructured text
    if not sections['skills'] and not sections['experience'] and not sections['education']:
        sections['other'] = text
    
    return sections


def compute_section_similarity(cv_section: str, job_section: str) -> float:
    """
    Compute cosine similarity between two text sections using embeddings.
    
    Phase 3: Per-section similarity computation
    
    Args:
        cv_section: Text from CV section
        job_section: Text from job description section
        
    Returns:
        Similarity score (0-100)
    """
    # Handle empty sections
    if not cv_section.strip() or not job_section.strip():
        return 0.0
    
    try:
        # Preprocess texts
        cv_preprocessed = preprocess_text(cv_section)
        job_preprocessed = preprocess_text(job_section)
        
        # Generate embeddings
        cv_embedding = get_embedding(cv_preprocessed)
        job_embedding = get_embedding(job_preprocessed)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(cv_embedding, job_embedding)
        
        # Convert to 0-100 scale
        similarity_score = max(0, min(100, similarity * 100))
        
        return round(similarity_score, 2)
        
    except Exception as e:
        logger.error(f"Error computing section similarity: {str(e)}")
        return 0.0


def compute_similarity(cv_text: str, job_description: str) -> Dict:
    """
    Compute deterministic similarity score between CV and job description.
    
    Phase 1: Embeddings + Cosine Similarity
    Phase 2: Keyword/Skills Extraction and Matching
    
    This function:
    1. Preprocesses both texts for consistency
    2. Generates embeddings using Gemini Embeddings API
    3. Calculates cosine similarity (deterministic vector math)
    4. Applies keyword matching to adjust score
    5. Extracts keywords from job description (Phase 2)
    6. Checks which keywords are present/missing in CV (Phase 2)
    7. Combines embedding similarity with keyword match ratio
    
    Args:
        cv_text: The candidate's CV text
        job_description: The job description text
        
    Returns:
        Dictionary containing:
            - similarity_score: float (0-100)
            - matched_keywords: List[str]
            - missing_keywords: List[str]
    """
    try:
        logger.info("Starting Phase 1+2 deterministic similarity computation")
        
        # Step 1: Preprocess texts
        cv_preprocessed = preprocess_text(cv_text)
        job_preprocessed = preprocess_text(job_description)
        
        logger.info(f"Preprocessed CV length: {len(cv_preprocessed)} chars")
        logger.info(f"Preprocessed JD length: {len(job_preprocessed)} chars")
        
        # Step 2: Extract keywords from job description FIRST (Phase 2)
        logger.info("Extracting keywords from job description...")
        job_keywords = extract_keywords_from_text(job_description)
        logger.info(f"Extracted {len(job_keywords)} keywords from job description")
        
        # Step 3: Match keywords against CV (Phase 2)
        logger.info("Matching keywords against CV...")
        matched_keywords, missing_keywords = match_keywords(cv_text, job_keywords)
        logger.info(f"Matched: {len(matched_keywords)}, Missing: {len(missing_keywords)}")
        
        # Calculate keyword match ratio
        keyword_match_ratio = 0.0
        if len(job_keywords) > 0:
            keyword_match_ratio = len(matched_keywords) / len(job_keywords)
            logger.info(f"Keyword match ratio: {keyword_match_ratio:.2%}")
        else:
            # If no keywords extracted, we need to rely more on embedding similarity
            # but be more conservative
            logger.warning("No keywords extracted from job description - using conservative scoring")
        
        # Step 4: Generate embeddings (Phase 1)
        logger.info("Generating CV embedding...")
        cv_embedding = get_embedding(cv_preprocessed)
        
        logger.info("Generating job description embedding...")
        job_embedding = get_embedding(job_preprocessed)
        
        # Step 5: Calculate cosine similarity (Phase 1)
        logger.info("Computing cosine similarity...")
        embedding_similarity = cosine_similarity(cv_embedding, job_embedding)
        
        # Convert to 0-100 scale
        embedding_score = max(0, min(100, embedding_similarity * 100))
        logger.info(f"Raw embedding similarity: {embedding_score:.2f}%")
        
        # Step 6: Combine embedding similarity with keyword matching
        # The final score is a weighted combination:
        # - If we have keywords: 40% embedding + 60% keyword matching
        # - If no keywords: Use embedding but apply stricter threshold
        
        if len(job_keywords) > 0:
            # We have keywords - use hybrid scoring
            keyword_score = keyword_match_ratio * 100
            
            # Adaptive weighting based on embedding similarity:
            # - High embedding (>80%): Trust it more, 50% embedding + 50% keyword
            # - Medium embedding (60-80%): Balanced, 40% embedding + 60% keyword  
            # - Low embedding (<60%): Trust keywords more, 30% embedding + 70% keyword
            
            if embedding_score >= 80:
                # High semantic similarity - give equal weight
                embedding_weight = 0.50
                keyword_weight = 0.50
            elif embedding_score >= 60:
                # Medium semantic similarity - keywords slightly more important
                embedding_weight = 0.40
                keyword_weight = 0.60
            else:
                # Low semantic similarity - keywords much more important
                embedding_weight = 0.30
                keyword_weight = 0.70
            
            final_score = (embedding_weight * embedding_score) + (keyword_weight * keyword_score)
            
            logger.info(f"Hybrid scoring: embedding={embedding_score:.2f}% (weight={embedding_weight}), "
                       f"keyword={keyword_score:.2f}% (weight={keyword_weight}), final={final_score:.2f}%")
            
            # Apply penalty if embedding similarity is very low (< 40%)
            # This catches cases where keywords might match by accident
            # but the overall content is unrelated
            if embedding_score < 40:
                penalty_factor = embedding_score / 40  # Scale from 0 to 1
                final_score = final_score * penalty_factor
                logger.info(f"Applied low embedding penalty: final score adjusted to {final_score:.2f}%")
            
        else:
            # No keywords extracted - be very conservative with embedding-only score
            # This usually means the job description is garbage/random text
            # Apply a very strict penalty to prevent false positives
            if embedding_score < 80:
                # For scores below 80%, apply very aggressive cubic penalty
                # This makes low-medium scores much lower
                # 70% -> 40.35%, 60% -> 24.88%, 50% -> 13.57%, 40% -> 6.35%
                normalized = embedding_score / 100
                final_score = (normalized ** 3) * 100
                logger.info(f"No keywords + low embedding: applied aggressive penalty, final={final_score:.2f}%")
            else:
                final_score = embedding_score
        
        # Ensure score is within bounds
        final_score = max(0, min(100, final_score))
        
        logger.info(f"Final similarity score: {final_score:.2f}%")
        
        return {
            "similarity_score": round(final_score, 2),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords
        }
        
    except Exception as e:
        logger.error(f"Error in compute_similarity: {str(e)}")
        raise Exception(f"Similarity computation failed: {str(e)}")


def compute_similarity_with_sections(cv_text: str, job_description: str, 
                                     use_weighted: bool = True) -> Dict:
    """
    Compute similarity with section-based breakdown.
    
    Phase 3: Section-Based Similarity Analysis
    
    This function:
    1. Detects sections in both CV and job description (skills, experience, education)
    2. Computes similarity for each section separately
    3. Computes overall similarity from full documents
    4. Optionally uses weighted aggregation based on section importance
    5. Includes Phase 2 keyword analysis
    
    Args:
        cv_text: The candidate's CV text
        job_description: The job description text
        use_weighted: If True, use weighted average for section scores (default: True)
        
    Returns:
        Dictionary containing:
            - overall_similarity: float (0-100) - from full document comparison
            - sections: Dict with similarity scores for each section
            - matched_keywords: List[str]
            - missing_keywords: List[str]
            - aggregated_similarity: float (0-100) - weighted average of sections
    """
    try:
        logger.info("Starting Phase 3 section-based similarity computation")
        
        # Step 1: Detect sections in both documents
        logger.info("Detecting sections in CV...")
        cv_sections = detect_sections(cv_text)
        
        logger.info("Detecting sections in job description...")
        job_sections = detect_sections(job_description)
        
        # Log detected sections
        for section_name, content in cv_sections.items():
            if content:
                logger.info(f"CV {section_name}: {len(content)} chars")
        
        for section_name, content in job_sections.items():
            if content:
                logger.info(f"Job {section_name}: {len(content)} chars")
        
        # Step 2: Compute similarity for each section
        section_scores = {}
        
        for section_name in ['skills', 'experience', 'education']:
            logger.info(f"Computing similarity for {section_name} section...")
            cv_section = cv_sections.get(section_name, '')
            job_section = job_sections.get(section_name, '')
            
            if cv_section and job_section:
                score = compute_section_similarity(cv_section, job_section)
                section_scores[section_name] = score
                logger.info(f"{section_name.capitalize()} similarity: {score:.2f}%")
            else:
                # If either section is empty, we can't compute similarity
                section_scores[section_name] = None
                logger.info(f"{section_name.capitalize()} section: No data to compare")
        
        # Step 3: Compute overall similarity from full documents
        logger.info("Computing overall document similarity...")
        overall_result = compute_similarity(cv_text, job_description)
        overall_similarity = overall_result['similarity_score']
        
        # Step 4: Compute aggregated similarity from sections
        # Use weighted average if requested, otherwise simple average
        weights = {
            'skills': 0.4,      # Skills are most important
            'experience': 0.4,  # Experience is equally important
            'education': 0.2    # Education is less critical
        }
        
        # Calculate weighted or simple average
        valid_sections = {k: v for k, v in section_scores.items() if v is not None}
        
        if valid_sections:
            if use_weighted:
                # Weighted average (only for sections that exist)
                total_weight = sum(weights[k] for k in valid_sections.keys())
                aggregated_similarity = sum(
                    section_scores[k] * weights[k] for k in valid_sections.keys()
                ) / total_weight
            else:
                # Simple average
                aggregated_similarity = sum(valid_sections.values()) / len(valid_sections)
            
            aggregated_similarity = round(aggregated_similarity, 2)
            logger.info(f"Aggregated section similarity: {aggregated_similarity:.2f}%")
        else:
            # If no sections were detected, use overall similarity
            aggregated_similarity = overall_similarity
            logger.info("No sections detected, using overall similarity as aggregated score")
        
        # Step 5: Get keyword analysis from Phase 2
        matched_keywords = overall_result['matched_keywords']
        missing_keywords = overall_result['missing_keywords']
        
        return {
            "overall_similarity": overall_similarity,
            "sections": section_scores,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "aggregated_similarity": aggregated_similarity
        }
        
    except Exception as e:
        logger.error(f"Error in compute_similarity_with_sections: {str(e)}")
        raise Exception(f"Section-based similarity computation failed: {str(e)}")


def get_phase4_stats() -> Dict:
    """
    Get Phase 4 optimization statistics.
    
    Returns:
        Dictionary with cache and usage statistics
    """
    return {
        'cache': _embedding_cache.get_stats(),
        'cache_size': _embedding_cache.get_cache_size(),
        'usage': _usage_tracker.get_usage_summary()
    }


def clear_cache() -> Dict:
    """
    Clear the embedding cache.
    
    Returns:
        Dictionary with information about cleared cache
    """
    files_deleted = _embedding_cache.clear()
    return {
        'files_deleted': files_deleted,
        'message': f"Cleared {files_deleted} cached embeddings"
    }


def batch_compute_embeddings(texts: List[str], use_cache: bool = True) -> List[np.ndarray]:
    """
    Compute embeddings for multiple texts efficiently.
    
    Phase 4: Batch processing for efficiency.
    
    Args:
        texts: List of texts to embed
        use_cache: If True, use caching for each embedding
        
    Returns:
        List of embedding vectors
    """
    embeddings = []
    
    logger.info(f"Batch processing {len(texts)} texts for embeddings...")
    
    for i, text in enumerate(texts):
        try:
            embedding = get_embedding(text, use_cache=use_cache)
            embeddings.append(embedding)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(texts)} embeddings")
                
        except Exception as e:
            logger.error(f"Failed to embed text {i}: {e}")
            # Return zero vector on failure
            embeddings.append(np.zeros(768))  # Default Gemini embedding dimension
    
    logger.info(f"Completed batch processing: {len(embeddings)} embeddings generated")
    
    # Log Phase 4 stats
    stats = get_phase4_stats()
    logger.info(f"Cache hit rate: {stats['cache']['hit_rate_percent']}%")
    logger.info(f"Total API requests: {stats['usage']['total']['requests']}")
    
    return embeddings


if __name__ == "__main__":
    # Test Phase 1+2
    print("=" * 60)
    print("Testing Phase 1+2: Basic Similarity + Keywords")
    print("=" * 60)
    
    test_cv = """
    John Doe
    Software Engineer
    
    Skills: Python, JavaScript, React, Node.js, PostgreSQL
    Experience: 5 years in web development
    Education: BS Computer Science
    """
    
    test_job = """
    Senior Software Engineer
    
    Requirements:
    - 3+ years of experience with Python
    - Experience with React and Node.js
    - Knowledge of databases (PostgreSQL preferred)
    - Docker and Kubernetes experience
    - BS in Computer Science or related field
    """
    
    result = compute_similarity(test_cv, test_job)
    print(f"\nPhase 1+2 Test Result:")
    print(f"Similarity Score: {result['similarity_score']}%")
    print(f"Matched Keywords: {result['matched_keywords']}")
    print(f"Missing Keywords: {result['missing_keywords']}")
    
    # Test Phase 3
    print("\n" + "=" * 60)
    print("Testing Phase 3: Section-Based Similarity")
    print("=" * 60)
    
    test_cv_structured = """
    John Doe
    Senior Software Engineer
    
    Skills:
    - Python, JavaScript, TypeScript
    - React, Node.js, Express
    - PostgreSQL, MongoDB, Redis
    - Docker, Kubernetes
    - AWS, CI/CD
    
    Experience:
    Software Engineer at Tech Corp (2019-2024)
    - Built scalable web applications using React and Node.js
    - Implemented microservices architecture with Docker and Kubernetes
    - Managed PostgreSQL databases and optimized queries
    - Deployed applications on AWS infrastructure
    
    Backend Developer at StartupXYZ (2016-2019)
    - Developed REST APIs using Python and Django
    - Worked with MongoDB and Redis for caching
    - Implemented CI/CD pipelines
    
    Education:
    BS in Computer Science, University of Technology (2012-2016)
    - GPA: 3.8/4.0
    - Focus on Software Engineering and Databases
    """
    
    test_job_structured = """
    Senior Software Engineer Position
    
    Skills:
    Required technical skills:
    - Strong proficiency in Python and JavaScript
    - Experience with React and modern frontend frameworks
    - Backend development with Node.js or Python
    - Database expertise (PostgreSQL, MongoDB)
    - Container orchestration (Docker, Kubernetes)
    - Cloud platforms (AWS preferred)
    
    Experience:
    We are looking for someone with:
    - 5+ years of software development experience
    - Proven track record building scalable web applications
    - Experience with microservices architecture
    - Strong understanding of database design and optimization
    - Experience with cloud infrastructure and deployment
    - CI/CD pipeline implementation experience
    
    Education:
    - BS/MS in Computer Science or related field
    - Strong academic background in software engineering
    """
    
    result_sections = compute_similarity_with_sections(test_cv_structured, test_job_structured)
    print(f"\nPhase 3 Test Result:")
    print(f"Overall Similarity (full documents): {result_sections['overall_similarity']}%")
    print(f"Aggregated Similarity (from sections): {result_sections['aggregated_similarity']}%")
    print(f"\nSection Breakdown:")
    for section, score in result_sections['sections'].items():
        if score is not None:
            print(f"  {section.capitalize()}: {score}%")
        else:
            print(f"  {section.capitalize()}: N/A (no data)")
    print(f"\nMatched Keywords: {result_sections['matched_keywords'][:10]}...")  # Show first 10
    print(f"Missing Keywords: {result_sections['missing_keywords']}")
