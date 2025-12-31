#!/usr/bin/env python3
"""
检查数据源在数据库中的启用状态
"""

import os
import sys
sys.path.append('.')

from tradingagents.dataflows.data_source_manager import DataSourceManager

def check_datasource_status():
    """检查数据源启用状态"""
    print("=== 数据源启用状态检查 ===")
    
    try:
        manager = DataSourceManager()
        available_sources = manager.get_available_sources()
        
        print(f"可用的数据源: {[source.value for source in available_sources]}")
        
        # 检查各个数据源的详细状态
        from app.core.database import get_mongo_db
        
        import asyncio
        async def check_db():
            db = get_mongo_db()
            
            # 检查数据源配置集合
            if 'datasource_configs' in db.list_collection_names():
                configs = db.datasource_configs.find({})
                print("\n数据库中的数据源配置:")
                for config in configs:
                    print(f"  - {config.get('name', 'unknown')}: {config}")
            else:
                print("\n数据库中没有找到 datasource_configs 集合")
                
            # 检查系统配置集合
            if 'system_configs' in db.list_collection_names():
                system_configs = db.system_configs.find({})
                print("\n系统配置:")
                for config in system_configs:
                    print(f"  - {config.get('config_key', 'unknown')}: {config.get('config_value', 'unknown')}")
            else:
                print("\n数据库中没有找到 system_configs 集合")
        
        asyncio.run(check_db())
        
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_datasource_status()
