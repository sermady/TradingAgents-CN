#!/usr/bin/env python3
"""
批量修复sys.path滥用

这个脚本会：
1. 扫描指定目录中的Python文件
2. 识别不必要的sys.path操作
3. 生成修复建议或自动修复
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 不需要修复的文件模式
SKIP_PATTERNS = [
    r'test_.*\.py$',       # 测试文件
    r'.*_test\.py$',       # 测试文件
    r'conftest\.py$',      # pytest配置
    r'.*__init__\.py$',    # 包初始化文件
]

# 需要保留sys.path的特殊情况
KEEP_SYS_PATH_PATTERNS = [
    r'web/',               # Streamlit应用需要
    r'scripts/',           # 工具脚本可以保留
]

def should_skip_file(file_path: Path) -> bool:
    """检查文件是否应该跳过"""
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, file_path.name):
            return True
    return False

def should_keep_sys_path(file_path: Path) -> bool:
    """检查文件是否应该保留sys.path"""
    file_str = str(file_path)
    for pattern in KEEP_SYS_PATH_PATTERNS:
        if pattern in file_str:
            return True
    return False

def find_sys_path_usage(directory: Path) -> List[Tuple[Path, List[Tuple[int, str]]]]:
    """
    查找所有使用sys.path的文件

    返回: [(文件路径, [(行号, 代码片段), ...]), ...]
    """
    results = []
    
    for py_file in directory.rglob('*.py'):
        if should_skip_file(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            usages = []
            for i, line in enumerate(lines, 1):
                if 'sys.path' in line and ('insert' in line or 'append' in line):
                    usages.append((i, line.strip()))
            
            if usages:
                results.append((py_file, usages))
        except Exception as e:
            print(f"警告：无法读取文件 {py_file}: {e}")
    
    return results

def generate_fix_report(directory: Path):
    """生成修复报告"""
    print("=" * 80)
    print("sys.path 使用情况报告")
    print("=" * 80)
    
    results = find_sys_path_usage(directory)
    
    if not results:
        print("\n[OK] No sys.path abuse found!")
        return
    
    keep_count = 0
    fix_count = 0
    
    for file_path, usages in results:
        if should_keep_sys_path(file_path):
            keep_count += 1
            print(f"\n[KEEP] {file_path} (保留 - Streamlit应用/工具脚本)")
            for line_no, line in usages:
                print(f"   L{line_no}: {line}")
        else:
            fix_count += 1
            print(f"\n[WARN] {file_path} (建议修复)")
            for line_no, line in usages:
                print(f"   L{line_no}: {line}")
    
    print("\n" + "=" * 80)
    print(f"Summary: Found {len(results)} files using sys.path")
    print(f"  - Keep: {keep_count} files (Streamlit apps/tools)")
    print(f"  - Suggest fix: {fix_count} files")
    print("=" * 80)

if __name__ == '__main__':
    import sys
    
    # 默认扫描项目根目录
    project_root = Path(__file__).parent.parent
    target_dir = project_root
    
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    
    if not target_dir.exists():
        print(f"错误：目录不存在: {target_dir}")
        sys.exit(1)
    
    generate_fix_report(target_dir)
    
    print("\nSuggestions:")
    print("1. For web/ dir: Streamlit apps can keep sys.path (optimized to relative imports)")
    print("2. For tests/ dir: Use pytest auto import")
    print("3. For scripts/ dir: Tool scripts can keep or use PYTHONPATH")
    print("4. For tradingagents/ and app/ dir: Should use standard package imports")
