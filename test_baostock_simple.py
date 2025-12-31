#!/usr/bin/env python3
"""
简单测试baostock API
"""

import baostock as bs
import pandas as pd

def test_baostock():
    print("=== Baostock API 测试 ===")
    
    # 登录
    lg = bs.login()
    print(f"登录结果: {lg.error_code} - {lg.error_msg}")
    
    if lg.error_code != '0':
        return
    
    try:
        # 测试 query_stock_basic 方法
        print("\n测试 query_stock_basic...")
        result = bs.query_stock_basic()
        
        data_list = []
        while (result.error_code == '0') & result.next():
            data_list.append(result.get_row_data())
        
        if data_list:
            df = pd.DataFrame(data_list, columns=result.fields)
            print(f"成功获取 {len(df)} 条股票数据")
            print("前3条数据:")
            print(df.head(3))
        else:
            print("未获取到数据")
    
    finally:
        # 登出
        lg_out = bs.logout()
        print(f"登出结果: {lg_out.error_code} - {lg_out.error_msg}")

if __name__ == "__main__":
    test_baostock()
