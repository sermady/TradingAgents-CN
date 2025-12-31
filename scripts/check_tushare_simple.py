#!/usr/bin/env python3
"""
简单检查Tushare配置
"""

import os

def check_tushare():
    print("=== Tushare Config Check ===")
    
    # Check environment variable
    token = os.getenv('TUSHARE_TOKEN')
    print(f"TUSHARE_TOKEN in env: {'SET' if token else 'NOT SET'}")
    if token:
        print(f"Token length: {len(token)} chars")
        print(f"Token preview: {token[:10]}...")
    
    # Test Tushare
    try:
        import tushare as ts
        if token:
            ts.set_token(token)
            api = ts.pro_api()
            result = api.stock_basic(list_status='L', limit=1)
            if result is not None and len(result) > 0:
                print("SUCCESS: Tushare token works!")
                return True
            else:
                print("FAILED: Tushare token invalid")
        else:
            print("FAILED: No token configured")
    except Exception as e:
        print(f"FAILED: Tushare error - {e}")
    
    return False

if __name__ == "__main__":
    check_tushare()
