"""
Phase 4: Usage Tracker Module
Tracks API usage, token counts, and costs to stay within budget.
"""

import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Tracks API usage and costs for Gemini API calls.
    
    Helps monitor:
    - Number of API calls
    - Estimated token usage
    - Cost estimation
    - Rate limiting
    """
    
    # Gemini API pricing (as of 2024 - verify current pricing)
    # gemini-embedding-001: Free tier limits
    PRICING = {
        'gemini-embedding-001': {
            'free_tier_requests_per_minute': 1500,
            'free_tier_requests_per_day': 50000,
            'cost_per_1k_tokens': 0.0  # Free tier
        },
        'gemini-2.5-flash': {
            'free_tier_requests_per_minute': 15,
            'free_tier_requests_per_day': 1500,
            'input_cost_per_1k_tokens': 0.0,  # Free tier
            'output_cost_per_1k_tokens': 0.0  # Free tier
        }
    }
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the usage tracker.
        
        Args:
            storage_path: Path to store usage data (default: ./cache/usage.json)
        """
        if storage_path is None:
            cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            storage_path = os.path.join(cache_dir, 'usage.json')
        
        self.storage_path = Path(storage_path)
        self.usage_data = self._load_usage_data()
        
        logger.info(f"Initialized UsageTracker at: {self.storage_path}")
    
    def _load_usage_data(self) -> Dict:
        """
        Load usage data from storage.
        
        Returns:
            Dictionary with usage data
        """
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load usage data: {e}")
        
        # Initialize empty usage data
        return {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'by_model': {},
            'by_date': {},
            'sessions': []
        }
    
    def _save_usage_data(self) -> None:
        """
        Save usage data to storage.
        """
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save usage data: {e}")
    
    def track_request(
        self,
        model: str,
        text_length: int,
        tokens: Optional[int] = None,
        cached: bool = False
    ) -> None:
        """
        Track an API request.
        
        Args:
            model: Name of the model used
            text_length: Length of the input text in characters
            tokens: Number of tokens (if known)
            cached: Whether the result was from cache
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Estimate tokens if not provided (rough estimate: ~4 chars per token)
        if tokens is None:
            tokens = max(1, text_length // 4)
        
        # Initialize model tracking if needed
        if model not in self.usage_data['by_model']:
            self.usage_data['by_model'][model] = {
                'requests': 0,
                'cached_requests': 0,
                'tokens': 0,
                'cost': 0.0
            }
        
        # Initialize date tracking if needed
        if today not in self.usage_data['by_date']:
            self.usage_data['by_date'][today] = {
                'requests': 0,
                'cached_requests': 0,
                'tokens': 0,
                'cost': 0.0
            }
        
        # Calculate cost (currently free tier, so $0)
        cost = 0.0
        if model in self.PRICING:
            cost_per_1k = self.PRICING[model].get('cost_per_1k_tokens', 0.0)
            if 'input_cost_per_1k_tokens' in self.PRICING[model]:
                cost_per_1k = self.PRICING[model]['input_cost_per_1k_tokens']
            cost = (tokens / 1000) * cost_per_1k
        
        # Update totals
        if not cached:
            self.usage_data['total_requests'] += 1
            self.usage_data['total_tokens'] += tokens
            self.usage_data['total_cost'] += cost
            
            # Update by model
            self.usage_data['by_model'][model]['requests'] += 1
            self.usage_data['by_model'][model]['tokens'] += tokens
            self.usage_data['by_model'][model]['cost'] += cost
            
            # Update by date
            self.usage_data['by_date'][today]['requests'] += 1
            self.usage_data['by_date'][today]['tokens'] += tokens
            self.usage_data['by_date'][today]['cost'] += cost
        else:
            # Track cached requests separately
            self.usage_data['by_model'][model]['cached_requests'] += 1
            self.usage_data['by_date'][today]['cached_requests'] += 1
        
        # Save after each update
        self._save_usage_data()
        
        logger.debug(
            f"Tracked request: model={model}, tokens={tokens}, "
            f"cached={cached}, cost=${cost:.4f}"
        )
    
    def get_usage_summary(self) -> Dict:
        """
        Get a summary of API usage.
        
        Returns:
            Dictionary with usage summary
        """
        today = datetime.now().strftime('%Y-%m-%d')
        today_data = self.usage_data['by_date'].get(today, {
            'requests': 0,
            'cached_requests': 0,
            'tokens': 0,
            'cost': 0.0
        })
        
        # Calculate cache effectiveness
        total_model_requests = sum(
            model_data['requests'] for model_data in self.usage_data['by_model'].values()
        )
        total_cached_requests = sum(
            model_data['cached_requests'] for model_data in self.usage_data['by_model'].values()
        )
        total_requests = total_model_requests + total_cached_requests
        cache_hit_rate = (total_cached_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total': {
                'requests': self.usage_data['total_requests'],
                'tokens': self.usage_data['total_tokens'],
                'cost': round(self.usage_data['total_cost'], 4),
                'cached_requests': total_cached_requests,
                'cache_hit_rate_percent': round(cache_hit_rate, 2)
            },
            'today': {
                'requests': today_data['requests'],
                'cached_requests': today_data.get('cached_requests', 0),
                'tokens': today_data['tokens'],
                'cost': round(today_data['cost'], 4)
            },
            'by_model': {
                model: {
                    'requests': data['requests'],
                    'cached_requests': data.get('cached_requests', 0),
                    'tokens': data['tokens'],
                    'cost': round(data['cost'], 4)
                }
                for model, data in self.usage_data['by_model'].items()
            }
        }
    
    def check_rate_limits(self, model: str) -> Dict[str, bool]:
        """
        Check if we're approaching rate limits.
        
        Args:
            model: Model name to check limits for
            
        Returns:
            Dictionary with rate limit status
        """
        today = datetime.now().strftime('%Y-%m-%d')
        today_data = self.usage_data['by_date'].get(today, {'requests': 0})
        
        if model not in self.PRICING:
            return {
                'within_limits': True,
                'warning': False,
                'message': 'No rate limit data for this model'
            }
        
        pricing = self.PRICING[model]
        daily_limit = pricing.get('free_tier_requests_per_day', float('inf'))
        
        requests_today = today_data['requests']
        usage_percent = (requests_today / daily_limit * 100) if daily_limit != float('inf') else 0
        
        within_limits = requests_today < daily_limit
        warning = usage_percent > 80  # Warn if over 80% of daily limit
        
        return {
            'within_limits': within_limits,
            'warning': warning,
            'requests_today': requests_today,
            'daily_limit': daily_limit,
            'usage_percent': round(usage_percent, 2),
            'message': f"Using {requests_today}/{daily_limit} daily requests ({usage_percent:.1f}%)"
        }
    
    def reset_usage(self) -> None:
        """
        Reset all usage data. Use with caution!
        """
        self.usage_data = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'by_model': {},
            'by_date': {},
            'sessions': []
        }
        self._save_usage_data()
        logger.info("Reset all usage data")


# Global tracker instance
_tracker_instance: Optional[UsageTracker] = None


def get_tracker() -> UsageTracker:
    """
    Get or create the global tracker instance.
    
    Returns:
        UsageTracker instance
    """
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UsageTracker()
    return _tracker_instance
