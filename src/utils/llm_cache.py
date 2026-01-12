"""
LLM Response Cache - SQLite-based caching for LLM responses.
Reduces API costs and speeds up repeated similar queries.
"""

import sqlite3
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta


class LLMCache:
    """
    SQLite-based cache for LLM responses.
    
    Features:
    - Hash-based key generation from prompts
    - Configurable TTL (time-to-live)
    - Automatic cleanup of expired entries
    - Hit/miss statistics
    """
    
    # Default TTL values in hours
    DEFAULT_TTL_HOURS = 24
    VERSION_TTL_HOURS = 168  # 7 days for version lookups
    SPEC_TTL_HOURS = 12  # 12 hours for specs
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize cache with SQLite database."""
        if db_path is None:
            cache_dir = Path(__file__).parent.parent.parent / "cache"
            cache_dir.mkdir(exist_ok=True)
            db_path = str(cache_dir / "llm_cache.db")
        
        self.db_path = db_path
        self._init_db()
        self._stats = {"hits": 0, "misses": 0}
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at REAL NOT NULL,
                ttl_hours INTEGER NOT NULL,
                category TEXT DEFAULT 'general',
                prompt_preview TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON cache(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created ON cache(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_key(self, system_prompt: str, user_prompt: str, model: str = "") -> str:
        """Generate cache key from prompts using SHA256."""
        content = f"{model}:{system_prompt}:{user_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        model: str = ""
    ) -> Optional[str]:
        """
        Get cached response if exists and not expired.
        
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(system_prompt, user_prompt, model)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value, created_at, ttl_hours FROM cache WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            value, created_at, ttl_hours = row
            expiry_time = created_at + (ttl_hours * 3600)
            
            if time.time() < expiry_time:
                self._stats["hits"] += 1
                return value
            else:
                # Expired, delete it
                self._delete(key)
        
        self._stats["misses"] += 1
        return None
    
    def set(
        self,
        system_prompt: str,
        user_prompt: str,
        response: str,
        model: str = "",
        ttl_hours: int = None,
        category: str = "general"
    ) -> None:
        """
        Cache a response.
        
        Args:
            system_prompt: System prompt used
            user_prompt: User prompt used
            response: LLM response to cache
            model: Model name
            ttl_hours: Time-to-live in hours
            category: Cache category for organization
        """
        if ttl_hours is None:
            ttl_hours = self.DEFAULT_TTL_HOURS
        
        key = self._generate_key(system_prompt, user_prompt, model)
        prompt_preview = user_prompt[:100] if user_prompt else ""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cache 
            (key, value, created_at, ttl_hours, category, prompt_preview)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (key, response, time.time(), ttl_hours, category, prompt_preview))
        
        conn.commit()
        conn.close()
    
    def _delete(self, key: str) -> None:
        """Delete a cache entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
        conn.close()
    
    def clear_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete where current_time > created_at + (ttl_hours * 3600)
        cursor.execute("""
            DELETE FROM cache 
            WHERE (? - created_at) > (ttl_hours * 3600)
        """, (time.time(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_all(self) -> None:
        """Clear entire cache."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache")
        conn.commit()
        conn.close()
        self._stats = {"hits": 0, "misses": 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cache")
        total_entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) FROM cache GROUP BY category")
        by_category = dict(cursor.fetchall())
        
        conn.close()
        
        hit_rate = 0
        total_requests = self._stats["hits"] + self._stats["misses"]
        if total_requests > 0:
            hit_rate = (self._stats["hits"] / total_requests) * 100
        
        return {
            "total_entries": total_entries,
            "by_category": by_category,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "hit_rate_percent": round(hit_rate, 2)
        }


# Global cache instance
_cache_instance: Optional[LLMCache] = None


def get_llm_cache() -> LLMCache:
    """Get or create global LLM cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LLMCache()
    return _cache_instance


def cached_llm_call(
    system_prompt: str,
    user_prompt: str,
    llm_func,
    model: str = "",
    ttl_hours: int = 24,
    category: str = "general",
    use_cache: bool = True
) -> str:
    """
    Wrapper for LLM calls with caching.
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        llm_func: Function to call if cache miss (should return string)
        model: Model identifier
        ttl_hours: Cache TTL
        category: Cache category
        use_cache: Whether to use caching
    
    Returns:
        LLM response (from cache or fresh)
    """
    if not use_cache:
        return llm_func()
    
    cache = get_llm_cache()
    
    # Try cache first
    cached = cache.get(system_prompt, user_prompt, model)
    if cached is not None:
        return cached
    
    # Cache miss - call LLM
    response = llm_func()
    
    # Store in cache
    cache.set(
        system_prompt, 
        user_prompt, 
        response, 
        model=model,
        ttl_hours=ttl_hours,
        category=category
    )
    
    return response
