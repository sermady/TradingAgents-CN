#!/usr/bin/env python3
"""
修复Tushare Token问题
"""

import os
import sys
sys.path.append('.')

def check_tushare_config():
    """检查Tushare配置"""
    print("=== Tushare 配置检查 ===")
    
    # 1. 检查环境变量
    token_from_env = os.getenv('TUSHARE_TOKEN')
    print(f"环境变量 TUSHARE_TOKEN: {'已设置' if token_from_env else '未设置'}")
    if token_from_env:
        print(f"Token长度: {len(token_from_env)} 字符")
        print(f"Token前10位: {token_from_env[:10]}...")
    
    # 2. 检查数据库配置
    try:
        from app.core.database import get_mongo_db
        
        import asyncio
        async def check_db():
            db = get_mongo_db()
            
            # 检查datasource_configs集合
            if 'datasource_configs' in db.list_collection_names():
                tushare_config = db.datasource_configs.find_one({"name": "tushare"})
                if tushare_config:
                    api_key = tushare_config.get('api_key')
                    print(f"数据库配置 API Key: {'已设置' if api_key else '未设置'}")
                    if api_key:
                        print(f"数据库Token长度: {len(api_key)} 字符")
                        print(f"数据库Token前10位: {api_key[:10]}...")
                else:
                    print("数据库中未找到tushare配置")
            else:
                print("数据库中没有找到datasource_configs集合")
        
        asyncio.run(check_db())
        
    except Exception as e:
        print(f"数据库检查失败: {e}")
    
    # 3. 测试Tushare连接
    print("\n=== Tushare 连接测试 ===")
    try:
        import tushare as ts
        
        # 尝试使用环境变量的token
        if token_from_env:
            print("使用环境变量Token测试...")
            ts.set_token(token_from_env)
            api = ts.pro_api()
            result = api.stock_basic(list_status='L', limit=1)
            if result is not None and len(result) > 0:
                print("✅ 环境变量Token测试成功")
                return
            else:
                print("❌ 环境变量Token测试失败")
        
        # 尝试使用数据库配置的token
        try:
            from app.core.database import get_mongo_db
            
            async def test_db_token():
                db = get_mongo_db()
                tushare_config = db.datasource_configs.find_one({"name": "tushare"})
                if tushare_config and tushare_config.get('api_key'):
                    print("使用数据库配置Token测试...")
                    ts.set_token(tushare_config['api_key'])
                    api = ts.pro_api()
                    result = api.stock_basic(list_status='L', limit=1)
                    if result is not None and len(result) > 0:
                        print("✅ 数据库配置Token测试成功")
                        return True
                    else:
                        print("❌ 数据库配置Token测试失败")
                return False
            
            if asyncio.run(test_db_token()):
                return
                
        except Exception as e:
            print(f"数据库Token测试失败: {e}")
        
        print("❌ 所有Token测试都失败")
        
    except ImportError:
        print("❌ Tushare库未安装")
    except Exception as e:
        print(f"❌ Tushare测试失败: {e}")

def suggest_solution():
    """提供解决方案"""
    print("\n=== 解决方案建议 ===")
    print("1. 获取有效的Tushare Token:")
    print("   - 访问 https://tushare.pro/")
    print("   - 注册账号并登录")
    print("   - 在用户中心获取Token")
    print()
    print("2. 更新Token的方法:")
    print("   方法1 - 环境变量:")
    print("   export TUSHARE_TOKEN='your_token_here'")
    print()
    print("   方法2 - 数据库配置:")
    print("   通过Web界面或直接操作数据库更新datasource_configs集合")
    print()
    print("3. 如果不需要Tushare:")
    print("   - 可以在数据源管理中禁用Tushare")
    print("   - 系统会自动跳过对Tushare的健康检查")

if __name__ == "__main__":
    check_tushare_config()
    suggest_solution()
