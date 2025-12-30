#!/usr/bin/env python3
"""
临时脚本清理工具

识别并删除临时、调试、实验性脚本文件，保留核心运维脚本
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple, Set
from datetime import datetime


class ScriptCleanupTool:
    """脚本清理工具"""

    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.dry_run = dry_run
        self.scripts_dir = project_root / "scripts"
        self.files_to_delete = []
        self.files_to_keep = []

    # 保留的脚本模式
    KEEP_PATTERNS = {
        # 核心启动脚本
        "startup/",
        "deployment/",
        "docker/",

        # 维护脚本
        "maintenance/",
        "migrations/",

        # 安装和设置
        "setup/",
        "install/",

        # Git相关
        "git/",

        # 配置和验证
        "config/",
        "validation/",

        # 关键工具脚本（按名称）
        "easy_install",
        "docker_deployment_init",
        "docker_init",
        "export_config",
        "import_config",
        "system_config",
        "backup_",
        "restore_",
    }

    # 删除的脚本模式
    DELETE_PATTERNS = {
        # 调试脚本
        "debug_",
        "debug/",

        # 演示脚本
        "demo_",

        # 一次性检查脚本
        "check_",

        # 修复脚本（已应用）
        "fix_",

        # 测试脚本（应移至tests/）
        "test_",

        # 验证脚本（一次性）
        "validate_",

        # 开发实验脚本
        "development/",

        # 存档目录
        "archived/",

        # 临时版本脚本
        "0.1.",
        "v0.1.",
    }

    def should_keep(self, file_path: Path) -> Tuple[bool, str]:
        """
        判断是否应该保留文件

        Returns:
            (是否保留, 原因)
        """
        rel_path = file_path.relative_to(self.scripts_dir)
        path_str = str(rel_path).replace("\\", "/")

        # 检查保留模式
        for pattern in self.KEEP_PATTERNS:
            if pattern in path_str or path_str.startswith(pattern):
                return True, f"匹配保留模式: {pattern}"

        # 检查删除模式
        for pattern in self.DELETE_PATTERNS:
            if pattern in path_str or path_str.startswith(pattern):
                return False, f"匹配删除模式: {pattern}"

        # 默认保留
        return True, "默认保留"

    def scan_scripts(self) -> Tuple[List[Path], List[Path]]:
        """
        扫描scripts目录

        Returns:
            (要删除的文件列表, 要保留的文件列表)
        """
        to_delete = []
        to_keep = []

        for file_path in self.scripts_dir.rglob("*.py"):
            # 跳过__init__.py和__main__.py
            if file_path.name in ["__init__.py", "__main__.py"]:
                to_keep.append(file_path)
                continue

            should_keep, reason = self.should_keep(file_path)

            if should_keep:
                to_keep.append(file_path)
            else:
                to_delete.append(file_path)

        return to_delete, to_keep

    def categorize_files(self, files: List[Path]) -> dict:
        """分类文件"""
        categories = {
            "debug": [],
            "demo": [],
            "test": [],
            "check": [],
            "fix": [],
            "validate": [],
            "development": [],
            "archived": [],
            "version": [],
            "other": []
        }

        for file_path in files:
            rel_path = file_path.relative_to(self.scripts_dir)
            path_str = str(rel_path).lower()

            if "debug" in path_str or "/debug/" in path_str.replace("\\", "/"):
                categories["debug"].append(file_path)
            elif "demo" in path_str:
                categories["demo"].append(file_path)
            elif path_str.startswith("test_") or "/test" in path_str.replace("\\", "/"):
                categories["test"].append(file_path)
            elif path_str.startswith("check_"):
                categories["check"].append(file_path)
            elif path_str.startswith("fix_"):
                categories["fix"].append(file_path)
            elif path_str.startswith("validate_"):
                categories["validate"].append(file_path)
            elif "/development/" in path_str.replace("\\", "/"):
                categories["development"].append(file_path)
            elif "/archived/" in path_str.replace("\\", "/"):
                categories["archived"].append(file_path)
            elif "0.1." in path_str or "v0.1." in path_str:
                categories["version"].append(file_path)
            else:
                categories["other"].append(file_path)

        return categories

    def cleanup(self):
        """执行清理操作"""
        print("=" * 70)
        print("Scripts Cleanup Tool")
        print("=" * 70)
        print(f"Scripts directory: {self.scripts_dir}")
        print(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'EXECUTE'}")
        print()

        # 扫描文件
        to_delete, to_keep = self.scan_scripts()

        # 分类
        categorized = self.categorize_files(to_delete)

        # 显示统计
        print(f"Files to keep: {len(to_keep)}")
        print(f"Files to delete: {len(to_delete)}")
        print()

        # 显示分类详情
        print("Files to delete by category:")
        print("-" * 70)
        for category, files in categorized.items():
            if files:
                print(f"\n{category.upper()} ({len(files)} files):")
                for file_path in files[:5]:  # 只显示前5个
                    rel_path = file_path.relative_to(self.scripts_dir)
                    size_kb = file_path.stat().st_size / 1024
                    print(f"  - {rel_path} ({size_kb:.1f} KB)")

                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")

        # 计算总大小
        total_size = sum(f.stat().st_size for f in to_delete)
        print()
        print("-" * 70)
        print(f"Total size to free: {total_size / 1024:.1f} KB")

        # 执行删除
        if not self.dry_run:
            print()
            print("[EXECUTE] Deleting files...")
            deleted_count = 0

            for file_path in to_delete:
                try:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to delete {file_path}: {e}")

            print()
            print("=" * 70)
            print(f"Cleanup completed! Deleted {deleted_count} files")
            print("=" * 70)
        else:
            print()
            print("=" * 70)
            print("DRY RUN completed. To apply changes, run:")
            print("  python scripts/cleanup_temp_scripts.py --execute")
            print("=" * 70)


def main():
    """主函数"""
    import sys

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 检查是否要执行删除
    dry_run = "--execute" not in sys.argv

    # 创建清理器并执行
    cleaner = ScriptCleanupTool(project_root, dry_run=dry_run)
    cleaner.cleanup()


if __name__ == "__main__":
    main()
