"""
Phase 4: Embedding Cache Module
Provides caching functionality to reduce API calls and costs.
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    Cache for storing and retrieving embeddings to avoid redundant API calls.
    
    Uses file-based storage with SHA-256 hashing for cache keys.
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize the embedding cache.
        
        Args:
            cache_dir: Directory to store cache files (default: ./cache/embeddings)
        """
        if cache_dir is None:
            # Use a cache directory in the backend folder
            cache_dir = os.path.join(os.path.dirname(__file__), 'cache', 'embeddings')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Track cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0
        }
        
        logger.info(f"Initialized EmbeddingCache at: {self.cache_dir}")
    
    def _generate_cache_key(self, text: str, model: str = "gemini-embedding-001") -> str:
        """
        Generate a unique cache key for the given text and model.
        
        Args:
            text: The text to generate a key for
            model: The embedding model name
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        # Combine text and model to create unique key
        content = f"{model}:{text}"
        
        # Generate SHA-256 hash
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get the file path for a cache key.
        
        Args:
            cache_key: The cache key (hash)
            
        Returns:
            Path object for the cache file
        """
        # Use subdirectories based on first 2 characters of hash to avoid too many files in one dir
        subdir = cache_key[:2]
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(exist_ok=True)
        
        return cache_subdir / f"{cache_key}.json"
    
    def get(self, text: str, model: str = "gemini-embedding-001") -> Optional[np.ndarray]:
        """
        Retrieve an embedding from the cache.
        
        Args:
            text: The text to look up
            model: The embedding model name
            
        Returns:
            NumPy array with the embedding if found, None otherwise
        """
        cache_key = self._generate_cache_key(text, model)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                
                # Convert list back to numpy array
                embedding = np.array(data['embedding'])
                
                self.stats['hits'] += 1
                logger.debug(f"Cache hit for key: {cache_key[:16]}...")
                
                return embedding
                
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_path}: {e}")
                # If cache file is corrupted, delete it
                try:
                    cache_path.unlink()
                except:
                    pass
                
                self.stats['misses'] += 1
                return None
        
        self.stats['misses'] += 1
        logger.debug(f"Cache miss for key: {cache_key[:16]}...")
        return None
    
    def put(self, text: str, embedding: np.ndarray, model: str = "gemini-embedding-001") -> None:
        """
        Store an embedding in the cache.
        
        Args:
            text: The text that was embedded
            embedding: The embedding vector
            model: The embedding model name
        """
        cache_key = self._generate_cache_key(text, model)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Convert numpy array to list for JSON serialization
            data = {
                'model': model,
                'embedding': embedding.tolist(),
                'dimension': len(embedding),
                'text_length': len(text)
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            
            self.stats['saves'] += 1
            logger.debug(f"Cached embedding for key: {cache_key[:16]}...")
            
        except Exception as e:
            logger.warning(f"Failed to save cache file {cache_path}: {e}")
    
    def clear(self) -> int:
        """
        Clear all cached embeddings.
        
        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in self.cache_dir.rglob('*.json'):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {count} cache files")
        return count
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache hit/miss stats
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'saves': self.stats['saves'],
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2)
        }
    
    def get_cache_size(self) -> Dict:
        """
        Get information about cache size.
        
        Returns:
            Dictionary with cache size information
        """
        file_count = 0
        total_bytes = 0
        
        for cache_file in self.cache_dir.rglob('*.json'):
            file_count += 1
            total_bytes += cache_file.stat().st_size
        
        return {
            'file_count': file_count,
            'total_bytes': total_bytes,
            'total_mb': round(total_bytes / (1024 * 1024), 2)
        }


# Global cache instance
_cache_instance: Optional[EmbeddingCache] = None


def get_cache() -> EmbeddingCache:
    """
    Get or create the global cache instance.
    
    Returns:
        EmbeddingCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = EmbeddingCache()
    return _cache_instance
