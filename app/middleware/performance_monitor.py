"""
性能监控中间件

监控MongoDB查询性能、API响应时间、缓存命中率等关键性能指标
"""

import time
import logging
from typing import Callable
from functools import wraps
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self):
        self.query_times = defaultdict(list)  # 查询执行时间
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total": 0
        }
        self.api_response_times = defaultdict(list)
        self.slow_queries = []  # 慢查询记录

    def record_query(self, operation: str, duration_ms: float):
        """记录查询执行时间"""
        self.query_times[operation].append(duration_ms)

        # 记录慢查询 (>1000ms)
        if duration_ms > 1000:
            self.slow_queries.append({
                "operation": operation,
                "duration_ms": duration_ms,
                "timestamp": time.time()
            })

            # 只保留最近100条慢查询
            if len(self.slow_queries) > 100:
                self.slow_queries.pop(0)

    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_stats["hits"] += 1
        self.cache_stats["total"] += 1

    def record_cache_miss(self):
        """记录缓存未命中"""
        self.cache_stats["misses"] += 1
        self.cache_stats["total"] += 1

    def record_api_response(self, endpoint: str, duration_ms: float):
        """记录API响应时间"""
        self.api_response_times[endpoint].append(duration_ms)

    def get_cache_hit_rate(self) -> float:
        """获取缓存命中率"""
        if self.cache_stats["total"] == 0:
            return 0.0
        return (self.cache_stats["hits"] / self.cache_stats["total"]) * 100

    def get_average_query_time(self, operation: str) -> float:
        """获取平均查询时间"""
        times = self.query_times.get(operation, [])
        if not times:
            return 0.0
        return sum(times) / len(times)

    def get_average_response_time(self, endpoint: str) -> float:
        """获取平均API响应时间"""
        times = self.api_response_times.get(endpoint, [])
        if not times:
            return 0.0
        return sum(times) / len(times)

    def get_summary(self) -> dict:
        """获取性能摘要"""
        summary = {
            "cache_hit_rate": self.get_cache_hit_rate(),
            "cache_stats": self.cache_stats.copy(),
            "slow_queries_count": len(self.slow_queries),
            "operations": {}
        }

        # 添加各操作的平均查询时间
        for operation, times in self.query_times.items():
            if times:
                summary["operations"][operation] = {
                    "avg_time_ms": sum(times) / len(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "count": len(times)
                }

        return summary


# 全局性能指标实例
performance_metrics = PerformanceMetrics()


def monitor_query_performance(operation_name: str = None):
    """
    监控查询性能的装饰器

    Args:
        operation_name: 操作名称，如果为None则使用函数名
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                performance_metrics.record_query(op_name, duration_ms)

                # 警告慢查询
                if duration_ms > 1000:
                    logger.warning(
                        f"[PERF] Slow query detected: {op_name} "
                        f"took {duration_ms:.2f}ms"
                    )
                elif duration_ms > 500:
                    logger.debug(
                        f"[PERF] Query {op_name} took {duration_ms:.2f}ms"
                    )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"[PERF] Query {op_name} failed after {duration_ms:.2f}ms: {e}"
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                performance_metrics.record_query(op_name, duration_ms)

                if duration_ms > 1000:
                    logger.warning(
                        f"[PERF] Slow query detected: {op_name} "
                        f"took {duration_ms:.2f}ms"
                    )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"[PERF] Query {op_name} failed after {duration_ms:.2f}ms: {e}"
                )
                raise

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class CacheMonitor:
    """缓存监控器"""

    @staticmethod
    def monitor_cache_hit(func: Callable):
        """监控缓存命中的装饰器"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # 假设返回None表示缓存未命中
            if result is None:
                performance_metrics.record_cache_miss()
            else:
                performance_metrics.record_cache_hit()

            return result

        return wrapper

    @staticmethod
    def get_cache_report() -> dict:
        """获取缓存报告"""
        return {
            "hit_rate": performance_metrics.get_cache_hit_rate(),
            "hits": performance_metrics.cache_stats["hits"],
            "misses": performance_metrics.cache_stats["misses"],
            "total": performance_metrics.cache_stats["total"]
        }


def log_performance_summary():
    """记录性能摘要日志"""
    summary = performance_metrics.get_summary()

    logger.info("=" * 60)
    logger.info("Performance Metrics Summary")
    logger.info("=" * 60)
    logger.info(f"Cache Hit Rate: {summary['cache_hit_rate']:.2f}%")
    logger.info(
        f"Cache Stats: {summary['cache_stats']['hits']} hits, "
        f"{summary['cache_stats']['misses']} misses"
    )
    logger.info(f"Slow Queries: {summary['slow_queries_count']}")

    if summary["operations"]:
        logger.info("\nOperation Performance:")
        for op, stats in summary["operations"].items():
            logger.info(
                f"  {op}: "
                f"avg={stats['avg_time_ms']:.2f}ms, "
                f"min={stats['min_time_ms']:.2f}ms, "
                f"max={stats['max_time_ms']:.2f}ms, "
                f"count={stats['count']}"
            )

    logger.info("=" * 60)
