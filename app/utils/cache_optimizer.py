"""
智能缓存策略优化器

实现多级缓存、智能缓存失效、缓存预热等功能
"""

import time
import asyncio
import hashlib
import json
import logging
from typing import Any, Optional, Callable, Dict, List
from functools import wraps
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger(__name__)


class CacheEntry:
    """缓存条目"""

    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # 生存时间(秒)
        self.hits = 0
        self.last_access = time.time()

    def is_expired(self) -> bool:
        """检查是否过期"""
        return (time.time() - self.created_at) > self.ttl

    def touch(self):
        """更新最后访问时间"""
        self.last_access = time.time()
        self.hits += 1


class LRUCache:
    """LRU缓存实现"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]

        # 检查是否过期
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None

        # 更新访问顺序(LRU)
        self.cache.move_to_end(key)
        entry.touch()
        self.hits += 1

        return entry.value

    def set(self, key: str, value: Any, ttl: int = 3600):
        """设置缓存值"""
        # 如果已存在，更新并移动到末尾
        if key in self.cache:
            self.cache[key].value = value
            self.cache[key].ttl = ttl
            self.cache.move_to_end(key)
            return

        # 检查是否需要淘汰
        if len(self.cache) >= self.max_size:
            # 移除最旧的条目
            self.cache.popitem(last=False)

        # 添加新条目
        self.cache[key] = CacheEntry(key, value, ttl)
        self.cache.move_to_end(key)

    def delete(self, key: str):
        """删除缓存条目"""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()

    def get_stats(self) -> dict:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }


class MultiLevelCache:
    """多级缓存系统"""

    def __init__(self):
        # L1: 内存缓存 (最快，容量小)
        self.l1_cache = LRUCache(max_size=100)

        # L2: Redis缓存 (快速，容量中等)
        self.redis_enabled = False
        self.redis_client = None

        # 缓存策略配置
        self.cache_policies = {
            "stock_info": {"ttl": 3600, "level": "l1"},  # 1小时
            "stock_quotes": {"ttl": 60, "level": "l1"},  # 1分钟
            "analysis_result": {"ttl": 7200, "level": "l2"},  # 2小时
            "user_settings": {"ttl": 1800, "level": "l2"},  # 30分钟
            "market_data": {"ttl": 300, "level": "l1"},  # 5分钟
        }

    async def init_redis(self, redis_client):
        """初始化Redis连接"""
        try:
            self.redis_client = redis_client
            await self.redis_client.ping()
            self.redis_enabled = True
            logger.info("Multi-level cache: Redis L2 cache enabled")
        except Exception as e:
            logger.warning(f"Multi-level cache: Redis disabled, using L1 only: {e}")
            self.redis_enabled = False

    def _generate_key(self, prefix: str, params: dict) -> str:
        """生成缓存键"""
        # 对参数进行排序和序列化以生成一致的键
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"

    async def get(self, prefix: str, params: dict) -> Optional[Any]:
        """获取缓存值"""
        policy = self.cache_policies.get(prefix, {"ttl": 3600, "level": "l1"})
        key = self._generate_key(prefix, params)

        # L1缓存
        if policy["level"] in ["l1", "l2"]:
            value = self.l1_cache.get(key)
            if value is not None:
                logger.debug(f"[L1] Cache hit: {key}")
                return value

        # L2缓存 (Redis)
        if policy["level"] == "l2" and self.redis_enabled:
            try:
                cached = await self.redis_client.get(key)
                if cached:
                    logger.debug(f"[L2] Cache hit: {key}")
                    value = json.loads(cached)
                    # 回填L1缓存
                    self.l1_cache.set(key, value, policy["ttl"])
                    return value
            except Exception as e:
                logger.warning(f"[L2] Cache get failed: {e}")

        return None

    async def set(self, prefix: str, params: dict, value: Any):
        """设置缓存值"""
        policy = self.cache_policies.get(prefix, {"ttl": 3600, "level": "l1"})
        key = self._generate_key(prefix, params)

        # L1缓存
        if policy["level"] in ["l1", "l2"]:
            self.l1_cache.set(key, value, policy["ttl"])

        # L2缓存 (Redis)
        if policy["level"] == "l2" and self.redis_enabled:
            try:
                await self.redis_client.setex(
                    key,
                    policy["ttl"],
                    json.dumps(value, default=str)
                )
                logger.debug(f"[L2] Cache set: {key}")
            except Exception as e:
                logger.warning(f"[L2] Cache set failed: {e}")

    async def invalidate(self, prefix: str, params: dict = None):
        """使缓存失效"""
        if params:
            # 使特定键失效
            key = self._generate_key(prefix, params)
            self.l1_cache.delete(key)

            if self.redis_enabled:
                try:
                    await self.redis_client.delete(key)
                except Exception as e:
                    logger.warning(f"Redis cache invalidation failed: {e}")
        else:
            # 使所有匹配前缀的键失效
            # 在L1缓存中查找匹配的键
            keys_to_delete = [k for k in self.l1_cache.cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                self.l1_cache.delete(key)

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            "l1_cache": self.l1_cache.get_stats(),
            "redis_enabled": self.redis_enabled
        }


# 全局多级缓存实例
multi_level_cache = MultiLevelCache()


def cached(prefix: str, ttl: int = 3600):
    """
    缓存装饰器

    Args:
        prefix: 缓存键前缀
        ttl: 生存时间(秒)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键参数
            cache_params = {
                "args": str(args),
                "kwargs": str(sorted(kwargs.items()))
            }

            # 尝试从缓存获取
            cached_value = await multi_level_cache.get(prefix, cache_params)
            if cached_value is not None:
                return cached_value

            # 执行函数
            result = await func(*args, **kwargs)

            # 存入缓存
            await multi_level_cache.set(prefix, cache_params, result)

            return result

        return wrapper

    return decorator


class CacheWarmer:
    """缓存预热器"""

    def __init__(self):
        self.warmup_tasks: List[Callable] = []

    def register_task(self, task: Callable):
        """注册预热任务"""
        self.warmup_tasks.append(task)

    async def warmup(self):
        """执行缓存预热"""
        logger.info("Starting cache warmup...")

        for task in self.warmup_tasks:
            try:
                await task()
                logger.info(f"Cache warmup task completed: {task.__name__}")
            except Exception as e:
                logger.error(f"Cache warmup task failed: {task.__name__}: {e}")

        logger.info("Cache warmup completed")


# 全局缓存预热器
cache_warmer = CacheWarmer()
