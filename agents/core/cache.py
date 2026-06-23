"""
MSRA Multi-Agent Framework - Multi-Level Cache System

本模块实现了多级缓存系统，支持内存缓存和磁盘缓存的自动穿透。

Author: MSRA Team
Version: 1.0.0
"""

import asyncio
import hashlib
from typing import Any, Optional, Dict, List, Callable, TYPE_CHECKING
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

from .interfaces import CacheEntry

if TYPE_CHECKING:
    from .interfaces import Task, TaskResult


# ========================================
# Cache Strategies
# ========================================

class CacheStrategy:
    """缓存策略基类"""

    def should_cache(self, key: str, value: Any) -> bool:
        """判断是否应该缓存"""
        return True

    def select_eviction(self, entries: List[CacheEntry]) -> List[str]:
        """选择淘汰的键"""
        return []


class LRUStrategy(CacheStrategy):
    """最近最少使用策略"""

    def select_eviction(self, entries: List[CacheEntry]) -> List[str]:
        if not entries:
            return []
        sorted_entries = sorted(entries, key=lambda e: e.accessed_at)
        count = max(1, len(entries) // 4)
        return [e.key for e in sorted_entries[:count]]


class LFUStrategy(CacheStrategy):
    """最不经常使用策略"""

    def select_eviction(self, entries: List[CacheEntry]) -> List[str]:
        if not entries:
            return []
        sorted_entries = sorted(entries, key=lambda e: e.access_count)
        count = max(1, len(entries) // 4)
        return [e.key for e in sorted_entries[:count]]


class TTLEvictionStrategy(CacheStrategy):
    """TTL过期策略"""

    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl

    def select_eviction(self, entries: List[CacheEntry]) -> List[str]:
        now = datetime.now()
        expired = []
        for e in entries:
            if e.ttl and now > e.created_at + timedelta(seconds=e.ttl):
                expired.append(e.key)
        return expired


# ========================================
# L1: Memory Cache
# ========================================

class MemoryCache:
    """L1: 内存缓存"""

    def __init__(
        self,
        max_size: int = 1000,
        strategy: Optional[CacheStrategy] = None
    ):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._strategy = strategy or LRUStrategy()
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired() and not entry.invalidated:
                    entry.accessed_at = datetime.now()
                    entry.access_count += 1
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry.value
                else:
                    del self._cache[key]

            self._misses += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """设置缓存"""
        async with self._lock:
            # 淘汰
            if len(self._cache) >= self._max_size:
                to_evict = self._strategy.select_eviction(list(self._cache.values()))
                for k in to_evict:
                    if k in self._cache:
                        del self._cache[k]

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl=ttl,
                tags=tags or []
            )
            self._cache[key] = entry

    async def invalidate(self, key: str) -> None:
        """失效指定键"""
        async with self._lock:
            if key in self._cache:
                self._cache[key].invalidated = True

    async def invalidate_by_tags(self, tags: List[str]) -> None:
        """按标签失效"""
        async with self._lock:
            for entry in self._cache.values():
                if any(t in entry.tags for t in tags):
                    entry.invalidated = True

    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
            "size": len(self._cache),
            "max_size": self._max_size
        }


# ========================================
# L2: Local Disk Cache
# ========================================

class LocalDiskCache:
    """L2: 本地磁盘缓存"""

    def __init__(
        self,
        cache_dir: str = "./.msra_cache",
        max_size_mb: int = 100,
        max_entries: int = 10000
    ):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._max_entries = max_entries
        self._index: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    def _get_file_path(self, key: str) -> Path:
        """获取文件路径"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.cache"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            if key not in self._index:
                self._misses += 1
                return None

            entry = self._index[key]
            if entry.is_expired() or entry.invalidated:
                await self._delete_entry(key)
                self._misses += 1
                return None

            file_path = self._get_file_path(key)
            if file_path.exists():
                try:
                    data = json.loads(file_path.read_text(encoding="utf-8"))
                    entry.accessed_at = datetime.now()
                    entry.access_count += 1
                    self._hits += 1
                    logger.debug(f"L2 cache hit for key: {key}")
                    return data
                except Exception as e:
                    logger.warning(f"L2 cache read error for key {key}: {e}")
                    await self._delete_entry(key)
                    self._misses += 1
                    return None

            self._misses += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """设置缓存"""
        async with self._lock:
            # 序列化数据
            try:
                serialized = json.dumps(value, ensure_ascii=False).encode("utf-8")
                size = len(serialized)
            except Exception as e:
                logger.warning(f"L2 cache serialization error for key {key}: {e}")
                return

            # 检查大小限制
            current_size = sum(
                e.size_bytes for e in self._index.values()
            )
            while (current_size + size > self._max_size_bytes or
                   len(self._index) >= self._max_entries):
                await self._evict_one()

            # 写入文件
            file_path = self._get_file_path(key)
            file_path.write_bytes(serialized)

            # 更新索引
            entry = CacheEntry(
                key=key,
                value=None,  # 不存储在内存中
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                ttl=ttl,
                tags=tags or [],
                size_bytes=size
            )
            self._index[key] = entry

    async def _delete_entry(self, key: str) -> None:
        """删除条目"""
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()
        if key in self._index:
            del self._index[key]

    async def _evict_one(self) -> None:
        """淘汰一个条目"""
        if not self._index:
            return

        # LRU淘汰
        oldest = min(self._index.values(), key=lambda e: e.accessed_at)
        await self._delete_entry(oldest.key)

    async def invalidate(self, key: str) -> None:
        """失效指定键"""
        async with self._lock:
            if key in self._index:
                self._index[key].invalidated = True

    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            for key in list(self._index.keys()):
                await self._delete_entry(key)
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self._hits + self._misses
        current_size = sum(e.size_bytes for e in self._index.values())
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
            "size_bytes": current_size,
            "max_size_bytes": self._max_size_bytes,
            "entries": len(self._index),
            "max_entries": self._max_entries
        }


# ========================================
# Multi-Level Cache
# ========================================

class MultiLevelCache:
    """多级缓存管理器"""

    def __init__(
        self,
        l1_size: int = 1000,
        l2_dir: str = "./.msra_cache",
        l2_size_mb: int = 100
    ):
        self.l1 = MemoryCache(max_size=l1_size)
        self.l2 = LocalDiskCache(cache_dir=l2_dir, max_size_mb=l2_size_mb)
        self._lock = asyncio.Lock()
        self._cache_metrics: Dict[str, Dict[str, int]] = {}

    async def get(
        self,
        key: str,
        tags: Optional[List[str]] = None,
        compute_if_missing: Optional[Callable] = None,
        ttl: Optional[int] = None
    ) -> Optional[Any]:
        """获取缓存，自动穿透多层"""

        # L1 查询
        value = await self.l1.get(key)
        if value is not None:
            self._record_hit("L1", key)
            return value

        # L2 查询
        value = await self.l2.get(key)
        if value is not None:
            # 回填L1
            await self.l1.set(key, value, ttl=ttl, tags=tags)
            self._record_hit("L2", key)
            return value

        # 未命中，计算并缓存
        if compute_if_missing:
            value = await compute_if_missing()
            if value is not None:
                await self.set(key, value, ttl=ttl, tags=tags)
                self._record_miss(key)
                return value

        self._record_miss(key)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """设置缓存，同时写入L1和L2"""
        await self.l1.set(key, value, ttl=ttl, tags=tags)
        await self.l2.set(key, value, ttl=ttl, tags=tags)

    async def invalidate(self, key: str) -> None:
        """失效指定键"""
        await self.l1.invalidate(key)
        await self.l2.invalidate(key)

    async def invalidate_by_tags(self, tags: List[str]) -> None:
        """按标签失效"""
        await self.l1.invalidate_by_tags(tags)
        # L2需要遍历索引，这里简化处理

    async def clear(self) -> None:
        """清空所有缓存"""
        await self.l1.clear()
        await self.l2.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "L1": self.l1.get_stats(),
            "L2": self.l2.get_stats(),
            "total_hits": sum(
                m["hits"] for m in self._cache_metrics.values()
            ),
            "total_misses": sum(
                m["misses"] for m in self._cache_metrics.values()
            )
        }

    def _record_hit(self, level: str, key: str) -> None:
        if level not in self._cache_metrics:
            self._cache_metrics[level] = {"hits": 0, "misses": 0}
        self._cache_metrics[level]["hits"] += 1

    def _record_miss(self, key: str) -> None:
        for level in self._cache_metrics:
            self._cache_metrics[level]["misses"] += 1


# ========================================
# Global Cache Instance
# ========================================

# 全局缓存实例
_global_cache: Optional[MultiLevelCache] = None


def get_cache() -> MultiLevelCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLevelCache()
    return _global_cache


def init_cache(
    l1_size: int = 1000,
    l2_dir: str = "./.msra_cache",
    l2_size_mb: int = 100
) -> MultiLevelCache:
    """初始化全局缓存"""
    global _global_cache
    _global_cache = MultiLevelCache(l1_size, l2_dir, l2_size_mb)
    return _global_cache


# ========================================
# Exports
# ========================================

__all__ = [
    "CacheStrategy",
    "LRUStrategy",
    "LFUStrategy",
    "TTLEvictionStrategy",
    "MemoryCache",
    "LocalDiskCache",
    "MultiLevelCache",
    "get_cache",
    "init_cache",
]
