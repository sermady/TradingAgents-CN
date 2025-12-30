"""
数据源健康监控系统
监控各个数据源的连接状态、性能指标和错误率
"""
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time

logger = logging.getLogger(__name__)


class DataSourceStatus(Enum):
    """数据源状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class HealthMetrics:
    """健康指标"""
    status: DataSourceStatus = DataSourceStatus.UNKNOWN
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0.0
    last_response_time: float = 0.0
    consecutive_failures: int = 0
    error_messages: List[str] = field(default_factory=list)
    last_check: Optional[datetime] = None


class DataSourceHealthMonitor:
    """数据源健康监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, HealthMetrics] = {}
        self.check_interval = 300  # 5分钟检查一次
        self.failure_threshold = 3  # 连续失败3次标记为不可用
        self.response_time_threshold = 30.0  # 响应时间超过30秒认为有问题
        self._monitoring_task: Optional[asyncio.Task] = None
        self._metrics_lock = threading.Lock()
        
    async def start_monitoring(self):
        """启动健康监控"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("[OK] 数据源健康监控已启动")
    
    async def stop_monitoring(self):
        """停止健康监控"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("⏹️ 数据源健康监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                await self.check_all_sources()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[FAIL] 健康监控循环异常: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再试
    
    async def check_all_sources(self):
        """检查所有数据源健康状态"""
        logger.info("[SEARCH] 开始数据源健康检查...")
        
        # 检查Tushare
        await self._check_tushare_health()
        
        # 检查AKShare  
        await self._check_akshare_health()
        
        # 检查BaoStock
        await self._check_baostock_health()
        
        # 检查MongoDB
        await self._check_mongodb_health()
        
        # 输出健康报告
        await self._generate_health_report()
    
    async def _check_tushare_health(self):
        """检查Tushare健康状态"""
        source_name = "tushare"
        start_time = time.time()
        
        try:
            def _check_sync() -> tuple[bool, Optional[str]]:
                # 尝试导入和测试Tushare（同步阻塞，必须放到线程）
                import tushare as ts
                from tradingagents.config.providers_config import get_provider_config

                config = get_provider_config("tushare")
                token = config.get('token')

                if not token:
                    return False, "Token未配置"

                # 设置token并测试连接
                ts.set_token(token)
                api = ts.pro_api()

                # 简单测试API调用
                result = api.stock_basic(list_status='L', limit=1)

                if result is not None and len(result) > 0:
                    return True, None
                return False, "API返回空结果"

            ok, err = await asyncio.to_thread(_check_sync)
            self._update_metrics(source_name, ok, err, time.time() - start_time)
            if ok:
                logger.debug(f"[OK] {source_name} 健康检查通过")
            else:
                logger.debug(f"[WARN] {source_name} 健康检查失败: {err}")
                
        except Exception as e:
            self._update_metrics(source_name, False, str(e), time.time() - start_time)
            logger.debug(f"[WARN] {source_name} 健康检查失败: {e}")
    
    async def _check_akshare_health(self):
        """检查AKShare健康状态"""
        source_name = "akshare"
        start_time = time.time()
        
        try:
            def _check_sync() -> tuple[bool, Optional[str]]:
                import akshare as ak
                result = ak.stock_info_a_code_name()
                if result is not None and len(result) > 0:
                    return True, None
                return False, "API返回空结果"

            ok, err = await asyncio.to_thread(_check_sync)
            self._update_metrics(source_name, ok, err, time.time() - start_time)
            if ok:
                logger.debug(f"[OK] {source_name} 健康检查通过")
            else:
                logger.debug(f"[WARN] {source_name} 健康检查失败: {err}")
                
        except Exception as e:
            self._update_metrics(source_name, False, str(e), time.time() - start_time)
            logger.debug(f"[WARN] {source_name} 健康检查失败: {e}")
    
    async def _check_baostock_health(self):
        """检查BaoStock健康状态"""
        source_name = "baostock"
        start_time = time.time()
        
        try:
            def _check_sync() -> tuple[bool, Optional[str]]:
                import baostock as bs
                lg = bs.login()
                try:
                    if lg.error_code != '0':
                        return False, f"登录失败: {lg.error_msg}"

                    rs = bs.query_sh_k_list()
                    if rs.error_code == '0':
                        return True, None
                    return False, f"查询失败: {rs.error_msg}"
                finally:
                    try:
                        bs.logout()
                    except Exception:
                        pass

            ok, err = await asyncio.to_thread(_check_sync)
            self._update_metrics(source_name, ok, err, time.time() - start_time)
            if ok:
                logger.debug(f"[OK] {source_name} 健康检查通过")
            else:
                logger.debug(f"[WARN] {source_name} 健康检查失败: {err}")
                
        except Exception as e:
            self._update_metrics(source_name, False, str(e), time.time() - start_time)
            logger.debug(f"[WARN] {source_name} 健康检查失败: {e}")
    
    async def _check_mongodb_health(self):
        """检查MongoDB健康状态"""
        source_name = "mongodb"
        start_time = time.time()
        
        try:
            from app.core.database import get_mongo_db_sync

            def _check_sync() -> tuple[bool, Optional[str]]:
                db = get_mongo_db_sync()
                result = db.client.admin.command('ping')
                if result.get('ok') == 1.0:
                    return True, None
                return False, "Ping失败"

            ok, err = await asyncio.to_thread(_check_sync)
            self._update_metrics(source_name, ok, err, time.time() - start_time)
            if ok:
                logger.debug(f"[OK] {source_name} 健康检查通过")
            else:
                logger.debug(f"[WARN] {source_name} 健康检查失败: {err}")
                
        except Exception as e:
            self._update_metrics(source_name, False, str(e), time.time() - start_time)
            logger.debug(f"[WARN] {source_name} 健康检查失败: {e}")
    
    def _update_metrics(self, source_name: str, success: bool, error_message: Optional[str], response_time: float):
        """更新健康指标"""
        with self._metrics_lock:
            if source_name not in self.metrics:
                self.metrics[source_name] = HealthMetrics()

            metrics = self.metrics[source_name]
            metrics.last_check = datetime.now()

            if success:
                metrics.success_count += 1
                metrics.last_success = datetime.now()
                metrics.consecutive_failures = 0
                metrics.last_response_time = response_time

                # 更新平均响应时间
                if metrics.avg_response_time == 0:
                    metrics.avg_response_time = response_time
                else:
                    metrics.avg_response_time = (metrics.avg_response_time + response_time) / 2

                # 更新状态
                if metrics.failure_count == 0:
                    metrics.status = DataSourceStatus.HEALTHY
                else:
                    metrics.status = DataSourceStatus.DEGRADED
            else:
                metrics.failure_count += 1
                metrics.last_failure = datetime.now()
                metrics.consecutive_failures += 1
                metrics.last_response_time = response_time

                # 记录错误信息（保留最近10条）
                if error_message:
                    metrics.error_messages.append(f"{datetime.now().strftime('%H:%M:%S')}: {error_message}")
                    if len(metrics.error_messages) > 10:
                        metrics.error_messages.pop(0)

                # 更新状态
                if metrics.consecutive_failures >= self.failure_threshold:
                    metrics.status = DataSourceStatus.UNAVAILABLE
                else:
                    metrics.status = DataSourceStatus.DEGRADED
    
    async def _generate_health_report(self):
        """生成健康报告"""
        logger.info("[CHART] 数据源健康报告:")
        
        for source_name, metrics in self.metrics.items():
            status_emoji = {
                DataSourceStatus.HEALTHY: "🟢",
                DataSourceStatus.DEGRADED: "🟡", 
                DataSourceStatus.UNAVAILABLE: "[REDIS]",
                DataSourceStatus.UNKNOWN: "⚪"
            }
            
            success_rate = 0
            if metrics.success_count + metrics.failure_count > 0:
                success_rate = metrics.success_count / (metrics.success_count + metrics.failure_count) * 100
            
            logger.info(f"  {status_emoji[metrics.status]} {source_name.upper()}:")
            logger.info(f"    状态: {metrics.status.value}")
            logger.info(f"    成功率: {success_rate:.1f}% ({metrics.success_count}成功/{metrics.failure_count}失败)")
            logger.info(f"    平均响应时间: {metrics.avg_response_time:.2f}秒")
            logger.info(f"    最后检查: {metrics.last_check.strftime('%H:%M:%S') if metrics.last_check else 'N/A'}")
            
            if metrics.consecutive_failures > 0:
                logger.info(f"    连续失败: {metrics.consecutive_failures}次")
            
            if metrics.error_messages:
                logger.info(f"    最近错误: {metrics.error_messages[-1]}")
    
    def get_health_status(self, source_name: str) -> DataSourceStatus:
        """获取数据源健康状态"""
        with self._metrics_lock:
            return self.metrics.get(source_name, HealthMetrics()).status
    
    def get_all_health_statuses(self) -> Dict[str, DataSourceStatus]:
        """获取所有数据源健康状态"""
        with self._metrics_lock:
            return {name: metrics.status for name, metrics in self.metrics.items()}
    
    def is_source_healthy(self, source_name: str) -> bool:
        """检查数据源是否健康"""
        status = self.get_health_status(source_name)
        return status == DataSourceStatus.HEALTHY
    
    def get_unhealthy_sources(self) -> List[str]:
        """获取不健康的数据源列表"""
        statuses = self.get_all_health_statuses()
        return [name for name, status in statuses.items() if status != DataSourceStatus.HEALTHY]


# 全局健康监控实例
health_monitor = DataSourceHealthMonitor()


async def start_health_monitoring():
    """启动健康监控"""
    await health_monitor.start_monitoring()


async def stop_health_monitoring():
    """停止健康监控"""
    await health_monitor.stop_monitoring()


def get_source_health_status(source_name: str) -> DataSourceStatus:
    """获取数据源健康状态"""
    return health_monitor.get_health_status(source_name)


def is_data_source_healthy(source_name: str) -> bool:
    """检查数据源是否健康"""
    return health_monitor.is_source_healthy(source_name)


_monitor_thread: Optional[threading.Thread] = None
_monitor_loop: Optional[asyncio.AbstractEventLoop] = None
_monitor_thread_lock = threading.Lock()


def start_health_monitoring_background():
    """在后台线程启动健康监控（幂等），用于同步环境或避免阻塞主事件循环。"""
    global _monitor_thread, _monitor_loop

    with _monitor_thread_lock:
        if _monitor_thread and _monitor_thread.is_alive():
            return

        def _run():
            global _monitor_loop
            loop = asyncio.new_event_loop()
            _monitor_loop = loop
            asyncio.set_event_loop(loop)

            # 启动监控（创建 monitoring task）
            loop.create_task(start_health_monitoring())

            try:
                loop.run_forever()
            finally:
                # 尽力清理，避免在退出时留下未回收的任务告警
                try:
                    pending = asyncio.all_tasks(loop=loop)
                    for t in pending:
                        t.cancel()
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                try:
                    loop.close()
                except Exception:
                    pass

        _monitor_thread = threading.Thread(
            target=_run,
            name="data_source_health_monitor",
            daemon=True,
        )
        _monitor_thread.start()


def stop_health_monitoring_background(timeout: float = 5.0):
    """停止后台健康监控线程（可选）。"""
    loop = _monitor_loop
    if loop and loop.is_running():
        try:
            fut = asyncio.run_coroutine_threadsafe(stop_health_monitoring(), loop)
            fut.result(timeout=timeout)
        except Exception:
            pass
        try:
            loop.call_soon_threadsafe(loop.stop)
        except Exception:
            pass
