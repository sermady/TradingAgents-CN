# TradingAgents-CN API 文档
> 自动生成时间: 2025-12-30 23:32:32

---
## 目录
- [akshare_init](#akshare_init)
- [analysis](#analysis)
- [auth_db](#auth_db)
- [baostock_init](#baostock_init)
- [cache](#cache)
- [config](#config)
- [database](#database)
- [favorites](#favorites)
- [financial_data](#financial_data)
- [health](#health)
- [historical_data](#historical_data)
- [internal_messages](#internal_messages)
- [logs](#logs)
- [model_capabilities](#model_capabilities)
- [multi_market_stocks](#multi_market_stocks)
- [multi_period_sync](#multi_period_sync)
- [multi_source_sync](#multi_source_sync)
- [news_data](#news_data)
- [notifications](#notifications)
- [operation_logs](#operation_logs)
- [paper](#paper)
- [queue](#queue)
- [reports](#reports)
- [scheduler](#scheduler)
- [screening](#screening)
- [social_media](#social_media)
- [sse](#sse)
- [stock_data](#stock_data)
- [stock_sync](#stock_sync)
- [stocks](#stocks)
- [sync](#sync)
- [system_config](#system_config)
- [tags](#tags)
- [tushare_init](#tushare_init)
- [usage_statistics](#usage_statistics)
- [websocket_notifications](#websocket_notifications)

---
## akshare_init
**文件**: `app/routers/akshare_init.py`

### API 端点

- **GET** - `@router.get("/status")`
- **GET** - `@router.get("/connection-test")`
- **POST** - `@router.post("/start-full")`
- **POST** - `@router.post("/start-basic-sync")`
- **GET** - `@router.get("/initialization-status")`
- **POST** - `@router.post("/stop")`

---
## analysis
**文件**: `app/routers/analysis.py`

### API 端点

- **POST** - `@router.post("/single", response_model=Dict[str, Any])`
- **GET** - `@router.get("/test-route")`
- **GET** - `@router.get("/tasks/{task_id}/status", response_model=Dict[str, Any])`
- **GET** - `@router.get("/tasks/{task_id}/result", response_model=Dict[str, Any])`
- **GET** - `@router.get("/tasks/all", response_model=Dict[str, Any])`
- **GET** - `@router.get("/tasks", response_model=Dict[str, Any])`
- **POST** - `@router.post("/batch", response_model=Dict[str, Any])`
- **POST** - `@router.post("/analyze")`
- **POST** - `@router.post("/analyze/batch")`
- **GET** - `@router.get("/batches/{batch_id}")`
- **POST** - `@router.post("/tasks/{task_id}/cancel")`
- **GET** - `@router.get("/user/queue-status")`
- **GET** - `@router.get("/user/history")`
- **GET** - `@router.get("/tasks/{task_id}/details")`
- **GET** - `@router.get("/admin/zombie-tasks")`
- **POST** - `@router.post("/admin/cleanup-zombie-tasks")`
- **POST** - `@router.post("/tasks/{task_id}/mark-failed")`
- **DELETE** - `@router.delete("/tasks/{task_id}")`

---
## auth_db
**文件**: `app/routers/auth_db.py`

### API 端点

- **POST** - `@router.post("/login")`
- **POST** - `@router.post("/refresh")`
- **POST** - `@router.post("/logout")`
- **GET** - `@router.get("/me")`
- **PUT** - `@router.put("/me")`
- **POST** - `@router.post("/change-password")`
- **POST** - `@router.post("/reset-password")`
- **POST** - `@router.post("/create-user")`
- **GET** - `@router.get("/users")`

---
## baostock_init
**文件**: `app/routers/baostock_init.py`

### API 端点

- **GET** - `@router.get("/status", response_model=Dict[str, Any])`
- **GET** - `@router.get("/connection-test", response_model=Dict[str, Any])`
- **POST** - `@router.post("/start-full", response_model=InitializationResponse)`
- **POST** - `@router.post("/start-basic", response_model=InitializationResponse)`
- **GET** - `@router.get("/initialization-status", response_model=Dict[str, Any])`
- **POST** - `@router.post("/stop", response_model=Dict[str, Any])`
- **GET** - `@router.get("/service-status", response_model=Dict[str, Any])`

---
## cache
**文件**: `app/routers/cache.py`

### API 端点

- **GET** - `@router.get("/stats")`
- **DELETE** - `@router.delete("/cleanup")`
- **DELETE** - `@router.delete("/clear")`
- **GET** - `@router.get("/details")`
- **GET** - `@router.get("/backend-info")`

---
## config
**文件**: `app/routers/config.py`

### API 端点

- **POST** - `@router.post("/reload", summary="重新加载配置")`
- **GET** - `@router.get("/system", response_model=SystemConfigResponse)`
- **GET** - `@router.get("/llm/providers", response_model=List[LLMProviderResponse])`
- **POST** - `@router.post("/llm/providers", response_model=dict)`
- **PUT** - `@router.put("/llm/providers/{provider_id}", response_model=dict)`
- **DELETE** - `@router.delete("/llm/providers/{provider_id}", response_model=dict)`
- **POST** - `@router.post("/llm/providers/{provider_id}/fetch-models", response_model=dict)`
- **POST** - `@router.post("/llm/providers/migrate-env", response_model=dict)`
- **POST** - `@router.post("/llm/providers/init-aggregators", response_model=dict)`
- **POST** - `@router.post("/llm/providers/{provider_id}/test", response_model=dict)`
- **POST** - `@router.post("/llm", response_model=dict)`
- **POST** - `@router.post("/datasource", response_model=dict)`
- **POST** - `@router.post("/database", response_model=dict)`
- **POST** - `@router.post("/test", response_model=ConfigTestResponse)`
- **POST** - `@router.post("/database/{db_name}/test", response_model=ConfigTestResponse)`
- **GET** - `@router.get("/llm", response_model=List[LLMConfig])`
- **DELETE** - `@router.delete("/llm/{provider}/{model_name}")`
- **POST** - `@router.post("/llm/set-default")`
- **GET** - `@router.get("/datasource", response_model=List[DataSourceConfig])`
- **PUT** - `@router.put("/datasource/{name}", response_model=dict)`
- **DELETE** - `@router.delete("/datasource/{name}", response_model=dict)`
- **GET** - `@router.get("/market-categories", response_model=List[MarketCategory])`
- **POST** - `@router.post("/market-categories", response_model=dict)`
- **PUT** - `@router.put("/market-categories/{category_id}", response_model=dict)`
- **DELETE** - `@router.delete("/market-categories/{category_id}", response_model=dict)`
- **GET** - `@router.get("/datasource-groupings", response_model=List[DataSourceGrouping])`
- **POST** - `@router.post("/datasource-groupings", response_model=dict)`
- **DELETE** - `@router.delete("/datasource-groupings/{data_source_name}/{category_id}", respons`
- **PUT** - `@router.put("/datasource-groupings/{data_source_name}/{category_id}", response_m`
- **PUT** - `@router.put("/market-categories/{category_id}/datasource-order", response_model=`
- **POST** - `@router.post("/datasource/set-default")`
- **GET** - `@router.get("/settings", response_model=Dict[str, Any])`
- **GET** - `@router.get("/settings/meta", response_model=dict)`
- **PUT** - `@router.put("/settings", response_model=dict)`
- **POST** - `@router.post("/export", response_model=dict)`
- **POST** - `@router.post("/import", response_model=dict)`
- **POST** - `@router.post("/migrate-legacy", response_model=dict)`
- **POST** - `@router.post("/default/llm", response_model=dict)`
- **POST** - `@router.post("/default/datasource", response_model=dict)`
- **GET** - `@router.get("/models", response_model=List[Dict[str, Any]])`
- **GET** - `@router.get("/model-catalog", response_model=List[Dict[str, Any]])`
- **GET** - `@router.get("/model-catalog/{provider}", response_model=Dict[str, Any])`
- **POST** - `@router.post("/model-catalog", response_model=dict)`
- **DELETE** - `@router.delete("/model-catalog/{provider}", response_model=dict)`
- **POST** - `@router.post("/model-catalog/init", response_model=dict)`
- **GET** - `@router.get("/database", response_model=List[DatabaseConfig])`
- **GET** - `@router.get("/database/{db_name}", response_model=DatabaseConfig)`
- **POST** - `@router.post("/database", response_model=dict)`
- **PUT** - `@router.put("/database/{db_name}", response_model=dict)`
- **DELETE** - `@router.delete("/database/{db_name}", response_model=dict)`

---
## database
**文件**: `app/routers/database.py`

### API 端点

- **GET** - `@router.get("/status")`
- **GET** - `@router.get("/stats")`
- **POST** - `@router.post("/test")`
- **POST** - `@router.post("/backup")`
- **GET** - `@router.get("/backups")`
- **POST** - `@router.post("/import")`
- **POST** - `@router.post("/export")`
- **DELETE** - `@router.delete("/backups/{backup_id}")`
- **POST** - `@router.post("/cleanup")`
- **POST** - `@router.post("/cleanup/analysis")`
- **POST** - `@router.post("/cleanup/logs")`

---
## favorites
**文件**: `app/routers/favorites.py`

### API 端点

- **GET** - `@router.get("/", response_model=dict)`
- **POST** - `@router.post("/", response_model=dict)`
- **PUT** - `@router.put("/{stock_code}", response_model=dict)`
- **DELETE** - `@router.delete("/{stock_code}", response_model=dict)`
- **GET** - `@router.get("/check/{stock_code}", response_model=dict)`
- **GET** - `@router.get("/tags", response_model=dict)`
- **POST** - `@router.post("/sync-realtime", response_model=dict)`

---
## financial_data
**文件**: `app/routers/financial_data.py`

### API 端点

- **GET** - `@router.get("/query/{symbol}", summary="查询股票财务数据")`
- **GET** - `@router.get("/latest/{symbol}", summary="获取最新财务数据")`
- **GET** - `@router.get("/statistics", summary="获取财务数据统计")`
- **POST** - `@router.post("/sync/start", summary="启动财务数据同步")`
- **POST** - `@router.post("/sync/single", summary="同步单只股票财务数据")`
- **GET** - `@router.get("/sync/statistics", summary="获取同步统计信息")`
- **GET** - `@router.get("/health", summary="财务数据服务健康检查")`

---
## health
**文件**: `app/routers/health.py`

### API 端点

- **GET** - `@router.get("/health")`
- **GET** - `@router.get("/healthz")`
- **GET** - `@router.get("/readyz")`

---
## historical_data
**文件**: `app/routers/historical_data.py`

### API 端点

- **GET** - `@router.get("/query/{symbol}", response_model=HistoricalDataResponse)`
- **POST** - `@router.post("/query", response_model=HistoricalDataResponse)`
- **GET** - `@router.get("/latest-date/{symbol}")`
- **GET** - `@router.get("/statistics")`
- **GET** - `@router.get("/compare/{symbol}")`
- **GET** - `@router.get("/health")`

---
## internal_messages
**文件**: `app/routers/internal_messages.py`

### API 端点

- **POST** - `@router.post("/save", response_model=dict)`
- **POST** - `@router.post("/query", response_model=dict)`
- **GET** - `@router.get("/latest/{symbol}", response_model=dict)`
- **GET** - `@router.get("/search", response_model=dict)`
- **GET** - `@router.get("/research-reports/{symbol}", response_model=dict)`
- **GET** - `@router.get("/analyst-notes/{symbol}", response_model=dict)`
- **GET** - `@router.get("/statistics", response_model=dict)`
- **GET** - `@router.get("/message-types", response_model=dict)`
- **GET** - `@router.get("/categories", response_model=dict)`
- **GET** - `@router.get("/health", response_model=dict)`

---
## logs
**文件**: `app/routers/logs.py`

### API 端点

- **GET** - `@router.get("/files", response_model=List[LogFileInfo])`
- **POST** - `@router.post("/read", response_model=LogContentResponse)`
- **POST** - `@router.post("/export")`
- **GET** - `@router.get("/statistics", response_model=LogStatisticsResponse)`
- **DELETE** - `@router.delete("/files/{filename}")`

---
## model_capabilities
**文件**: `app/routers/model_capabilities.py`

### API 端点

- **GET** - `@router.get("/default-configs")`
- **GET** - `@router.get("/depth-requirements", response_model=dict)`
- **GET** - `@router.get("/capability-descriptions", response_model=dict)`
- **GET** - `@router.get("/badges", response_model=dict)`
- **POST** - `@router.post("/recommend", response_model=dict)`
- **POST** - `@router.post("/validate", response_model=dict)`
- **POST** - `@router.post("/batch-init", response_model=dict)`
- **GET** - `@router.get("/model/{model_name}", response_model=dict)`

---
## multi_market_stocks
**文件**: `app/routers/multi_market_stocks.py`

### API 端点

- **GET** - `@router.get("", response_model=dict)`
- **GET** - `@router.get("/{market}/stocks/search", response_model=dict)`
- **GET** - `@router.get("/{market}/stocks/{code}/info", response_model=dict)`
- **GET** - `@router.get("/{market}/stocks/{code}/quote", response_model=dict)`
- **GET** - `@router.get("/{market}/stocks/{code}/daily", response_model=dict)`

---
## multi_period_sync
**文件**: `app/routers/multi_period_sync.py`

### API 端点

- **POST** - `@router.post("/start", response_model=MultiPeriodSyncResponse)`
- **POST** - `@router.post("/start-daily", response_model=MultiPeriodSyncResponse)`
- **POST** - `@router.post("/start-weekly", response_model=MultiPeriodSyncResponse)`
- **POST** - `@router.post("/start-monthly", response_model=MultiPeriodSyncResponse)`
- **POST** - `@router.post("/start-all-history", response_model=MultiPeriodSyncResponse)`
- **POST** - `@router.post("/start-incremental", response_model=MultiPeriodSyncResponse)`
- **GET** - `@router.get("/statistics")`
- **GET** - `@router.get("/period-comparison/{symbol}")`
- **GET** - `@router.get("/supported-periods")`
- **GET** - `@router.get("/health")`

---
## multi_source_sync
**文件**: `app/routers/multi_source_sync.py`

### API 端点

- **GET** - `@router.get("/sources/status")`
- **GET** - `@router.get("/sources/current")`
- **GET** - `@router.get("/status")`
- **POST** - `@router.post("/stock_basics/run")`
- **POST** - `@router.post("/test-sources")`
- **GET** - `@router.get("/recommendations")`
- **GET** - `@router.get("/history")`
- **DELETE** - `@router.delete("/cache")`

---
## news_data
**文件**: `app/routers/news_data.py`

### API 端点

- **GET** - `@router.get("/query/{symbol}", response_model=dict)`
- **POST** - `@router.post("/query", response_model=dict)`
- **GET** - `@router.get("/latest", response_model=dict)`
- **GET** - `@router.get("/search", response_model=dict)`
- **GET** - `@router.get("/statistics", response_model=dict)`
- **POST** - `@router.post("/sync/start", response_model=dict)`
- **POST** - `@router.post("/sync/single", response_model=dict)`
- **DELETE** - `@router.delete("/cleanup", response_model=dict)`
- **GET** - `@router.get("/health", response_model=dict)`

---
## notifications
**文件**: `app/routers/notifications.py`

### API 端点

- **GET** - `@router.get("/notifications")`
- **GET** - `@router.get("/notifications/unread_count")`
- **POST** - `@router.post("/notifications/{notif_id}/read")`
- **POST** - `@router.post("/notifications/read_all")`
- **GET** - `@router.get("/notifications/debug/redis_pool")`

---
## operation_logs
**文件**: `app/routers/operation_logs.py`

### API 端点

- **GET** - `@router.get("/list", response_model=OperationLogListResponse)`
- **GET** - `@router.get("/stats", response_model=OperationLogStatsResponse)`
- **GET** - `@router.get("/{log_id}")`
- **POST** - `@router.post("/clear", response_model=ClearLogsResponse)`
- **POST** - `@router.post("/create")`
- **GET** - `@router.get("/export/csv")`

---
## paper
**文件**: `app/routers/paper.py`

### API 端点

- **GET** - `@router.get("/account", response_model=dict)`
- **POST** - `@router.post("/order", response_model=dict)`
- **GET** - `@router.get("/positions", response_model=dict)`
- **GET** - `@router.get("/orders", response_model=dict)`
- **POST** - `@router.post("/reset", response_model=dict)`

---
## queue
**文件**: `app/routers/queue.py`

### API 端点

- **GET** - `@router.get("/stats")`

---
## reports
**文件**: `app/routers/reports.py`

### API 端点

- **GET** - `@router.get("/list", response_model=Dict[str, Any])`
- **GET** - `@router.get("/{report_id}/detail")`
- **GET** - `@router.get("/{report_id}/content/{module}")`
- **DELETE** - `@router.delete("/{report_id}")`
- **GET** - `@router.get("/{report_id}/download")`

---
## scheduler
**文件**: `app/routers/scheduler.py`

### API 端点

- **GET** - `@router.get("/jobs")`
- **PUT** - `@router.put("/jobs/{job_id}/metadata")`
- **GET** - `@router.get("/jobs/{job_id}")`
- **POST** - `@router.post("/jobs/{job_id}/pause")`
- **POST** - `@router.post("/jobs/{job_id}/resume")`
- **POST** - `@router.post("/jobs/{job_id}/trigger")`
- **GET** - `@router.get("/jobs/{job_id}/history")`
- **GET** - `@router.get("/history")`
- **GET** - `@router.get("/stats")`
- **GET** - `@router.get("/health")`
- **GET** - `@router.get("/executions")`
- **GET** - `@router.get("/jobs/{job_id}/executions")`
- **GET** - `@router.get("/jobs/{job_id}/execution-stats")`
- **POST** - `@router.post("/executions/{execution_id}/cancel")`
- **POST** - `@router.post("/executions/{execution_id}/mark-failed")`
- **DELETE** - `@router.delete("/executions/{execution_id}")`

---
## screening
**文件**: `app/routers/screening.py`

### API 端点

- **GET** - `@router.get("/fields", response_model=FieldConfigResponse)`
- **POST** - `@router.post("/run", response_model=ScreeningResponse)`
- **POST** - `@router.post("/enhanced", response_model=NewScreeningResponse)`
- **GET** - `@router.get("/fields", response_model=List[Dict[str, Any]])`
- **GET** - `@router.get("/fields/{field_name}", response_model=Dict[str, Any])`
- **POST** - `@router.post("/validate", response_model=Dict[str, Any])`
- **GET** - `@router.get("/industries")`

---
## social_media
**文件**: `app/routers/social_media.py`

### API 端点

- **POST** - `@router.post("/save", response_model=dict)`
- **POST** - `@router.post("/query", response_model=dict)`
- **GET** - `@router.get("/latest/{symbol}", response_model=dict)`
- **GET** - `@router.get("/search", response_model=dict)`
- **GET** - `@router.get("/statistics", response_model=dict)`
- **GET** - `@router.get("/platforms", response_model=dict)`
- **GET** - `@router.get("/sentiment-analysis/{symbol}", response_model=dict)`
- **GET** - `@router.get("/health", response_model=dict)`

---
## sse
**文件**: `app/routers/sse.py`

### API 端点

- **GET** - `@router.get("/tasks/{task_id}")`
- **GET** - `@router.get("/batches/{batch_id}")`

---
## stock_data
**文件**: `app/routers/stock_data.py`

### API 端点

- **GET** - `@router.get("/basic-info/{symbol}", response_model=StockBasicInfoResponse)`
- **GET** - `@router.get("/quotes/{symbol}", response_model=MarketQuotesResponse)`
- **GET** - `@router.get("/list", response_model=StockListResponse)`
- **GET** - `@router.get("/combined/{symbol}")`
- **GET** - `@router.get("/search")`
- **GET** - `@router.get("/markets")`
- **GET** - `@router.get("/sync-status/quotes")`

---
## stock_sync
**文件**: `app/routers/stock_sync.py`

### API 端点

- **POST** - `@router.post("/single")`
- **POST** - `@router.post("/batch")`
- **GET** - `@router.get("/status/{symbol}")`

---
## stocks
**文件**: `app/routers/stocks.py`

### API 端点

- **GET** - `@router.get("/{code}/quote", response_model=dict)`
- **GET** - `@router.get("/{code}/fundamentals", response_model=dict)`
- **GET** - `@router.get("/{code}/kline", response_model=dict)`
- **GET** - `@router.get("/{code}/news", response_model=dict)`

---
## sync
**文件**: `app/routers/sync.py`

### API 端点

- **POST** - `@router.post("/stock_basics/run")`
- **GET** - `@router.get("/stock_basics/status")`

---
## system_config
**文件**: `app/routers/system_config.py`

### API 端点

- **GET** - `@router.get("/config/summary", tags=["system"], summary="配置概要（已屏蔽敏感项，需管理员）")`
- **GET** - `@router.get("/config/validate", tags=["system"], summary="验证配置完整性")`

---
## tags
**文件**: `app/routers/tags.py`

### API 端点

- **GET** - `@router.get("/", response_model=dict)`
- **POST** - `@router.post("/", response_model=dict)`
- **PUT** - `@router.put("/{tag_id}", response_model=dict)`
- **DELETE** - `@router.delete("/{tag_id}", response_model=dict)`

---
## tushare_init
**文件**: `app/routers/tushare_init.py`

### API 端点

- **GET** - `@router.get("/status", response_model=dict)`
- **GET** - `@router.get("/initialization-status", response_model=dict)`
- **POST** - `@router.post("/start-basic", response_model=dict)`
- **POST** - `@router.post("/start-full", response_model=dict)`
- **POST** - `@router.post("/stop", response_model=dict)`

---
## usage_statistics
**文件**: `app/routers/usage_statistics.py`

### API 端点

- **GET** - `@router.get("/records", summary="获取使用记录")`
- **GET** - `@router.get("/statistics", summary="获取使用统计")`
- **GET** - `@router.get("/cost/by-provider", summary="按供应商统计成本")`
- **GET** - `@router.get("/cost/by-model", summary="按模型统计成本")`
- **GET** - `@router.get("/cost/daily", summary="每日成本统计")`
- **DELETE** - `@router.delete("/records/old", summary="删除旧记录")`

---
## websocket_notifications
**文件**: `app/routers/websocket_notifications.py`

### API 端点

- **GET** - `@router.get("/ws/stats")`

---
