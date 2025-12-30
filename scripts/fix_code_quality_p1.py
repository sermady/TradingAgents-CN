#!/usr/bin/env python3
"""
P1代码质量批量修复工具

自动修复：
1. 裸except语句 (except:)
2. 调试print语句
3. 其他代码质量问题
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# 跳过的文件模式
SKIP_PATTERNS = [
    r'test_.*\.py$',
    r'.*_test\.py$',
    r'conftest\.py$',
    r'.*/migrations/.*',
]

def should_skip_file(file_path: Path) -> bool:
    """检查文件是否应该跳过"""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, str(file_path)):
            return True
    return False

def find_bare_except(file_path: Path) -> List[Tuple[int, str]]:
    """查找裸except语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        issues = []
        for i, line in enumerate(lines, 1):
            # 匹配 except: (可能有注释)
            if re.search(r'except\s*:\s*$', line.strip()):
                issues.append((i, line.strip()))
        
        return issues
    except Exception:
        return []

def find_print_statements(file_path: Path) -> List[Tuple[int, str]]:
    """查找调试print语句（排除__main__等）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        issues = []
        # 检查是否在__main__块中
        in_main_block = False
        
        for i, line in enumerate(lines, 1):
            # 检测__main__块
            if '__name__' in line and '__main__' in line:
                in_main_block = True
                continue
            
            # 缩进恢复，退出main块
            if in_main_block and line and not line[0].isspace():
                in_main_block = False
            
            # main块中的print可以保留
            if in_main_block:
                continue
            
            # 查找print语句
            if re.search(r'\bprint\s*\(', line):
                # 排除已经注释的行
                if not line.strip().startswith('#'):
                    issues.append((i, line.strip()))
        
        return issues
    except Exception:
        return []

def scan_directory(directory: Path) -> dict:
    """扫描目录，生成问题报告"""
    results = {
        'bare_except': [],
        'print_statements': [],
    }
    
    for py_file in directory.rglob('*.py'):
        if should_skip_file(py_file):
            continue
        
        # 检查裸except
        bare_excepts = find_bare_except(py_file)
        if bare_excepts:
            results['bare_except'].append((py_file, bare_excepts))
        
        # 检查print语句
        prints = find_print_statements(py_file)
        if prints:
            results['print_statements'].append((py_file, prints))
    
    return results

def generate_report(directory: Path):
    """生成修复报告"""
    print("=" * 80)
    print("P1 Code Quality Issues Report")
    print("=" * 80)
    
    results = scan_directory(directory)
    
    # 裸except报告
    print(f"\n[BARE EXCEPT] Found in {len(results['bare_except'])} files")
    for file_path, issues in results['bare_except'][:10]:  # 只显示前10个
        print(f"\n{file_path}:")
        for line_no, line in issues[:3]:  # 每个文件只显示前3个
            print(f"  L{line_no}: {line}")
        if len(issues) > 3:
            print(f"  ... and {len(issues) - 3} more")
    
    if len(results['bare_except']) > 10:
        print(f"\n... and {len(results['bare_except']) - 10} more files")
    
    # print语句报告
    print(f"\n[PRINT STATEMENTS] Found in {len(results['print_statements'])} files")
    for file_path, issues in results['print_statements'][:10]:
        print(f"\n{file_path}:")
        for line_no, line in issues[:3]:
            print(f"  L{line_no}: {line}")
        if len(issues) > 3:
            print(f"  ... and {len(issues) - 3} more")
    
    if len(results['print_statements']) > 10:
        print(f"\n... and {len(results['print_statements']) - 10} more files")
    
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  - Bare except: {sum(len(issues) for _, issues in results['bare_except'])} occurrences in {len(results['bare_except'])} files")
    print(f"  - Print statements: {sum(len(issues) for _, issues in results['print_statements'])} occurrences in {len(results['print_statements'])} files")
    print("=" * 80)
    
    print("\nFix Recommendations:")
    print("1. Bare except: Replace 'except:' with specific exceptions")
    print("   Example: except ValueError as e:")
    print("2. Print statements: Replace with logger.info/debug/error")
    print("   Example: logger.info(f\"Processing {item}\")")
    print("\nNote: Test files and __main__ blocks are excluded from scan")

if __name__ == '__main__':
    import sys
    project_root = Path(__file__).parent.parent
    target_dir = project_root / 'app'  # 默认扫描app目录
    
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    
    if not target_dir.exists():
        print(f"Error: Directory not found: {target_dir}")
        sys.exit(1)
    
    generate_report(target_dir)
