#!/usr/bin/env python3
"""
文档归档和优化工具

识别并归档临时文档，建立文档版本管理策略
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime


class DocOrganizer:
    """文档整理器"""

    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.dry_run = dry_run
        self.archive_dir = self.docs_dir / "archive"
        self.files_to_archive = []
        self.files_to_keep = []

    # 保留的核心文档
    KEEP_PATTERNS = {
        # 核心文档
        "README.md",
        "QUICK_START.md",
        "STRUCTURE.md",

        # 安装指南
        "guides/INSTALLATION",
        "guides/installation",
        "guides/quick-start",
        "guides/docker-deployment",

        # API文档
        "api/",

        # 配置指南
        "configuration/",

        # 当前版本设计
        "design/v1.0.1/",

        # 用户指南
        "usage/",
        "guides/",
    }

    # 归档的临时文档
    ARCHIVE_PATTERNS = {
        # 旧版本修复文档
        "fixes/2025-10-",
        "fixes/2025-11-",

        # 临时分析
        "analysis/",

        # 技术评审草稿
        "tech_reviews/",

        # 旧版本设计
        "design/v0.1.",
        "design/timezone",

        # 版本特定文档
        "releases/v0.1.",
        "releases/VERSION_0.1.",

        # 临时修复摘要
        "bugfix/2025-10-",
        "bugfix/2025-11-",

        # 已解决问题
        "troubleshooting/windows_cairo_fix.md",
        "troubleshooting/windows10-chromadb-fix.md",
        "troubleshooting/stock_name_issue.md",
        "troubleshooting/streamlit-file-watcher-fix.md",

        # 旧博客
        "blog/2025-10-",
        "blog/2025-11-01",
        "blog/2025-11-0",
        "blog/2025-11-1",

        # 临时分析报告
        "summary/phase/",
        "summary/pe-pb-",

        # 旧架构文档
        "architecture/v0.1.",
    }

    def should_archive(self, file_path: Path) -> Tuple[bool, str]:
        """
        判断是否应该归档

        Returns:
            (是否归档, 原因)
        """
        rel_path = file_path.relative_to(self.docs_dir)
        path_str = str(rel_path).replace("\\", "/")

        # 检查保留模式
        for pattern in self.KEEP_PATTERNS:
            if pattern in path_str or path_str.startswith(pattern):
                return False, f"匹配保留模式: {pattern}"

        # 检查归档模式
        for pattern in self.ARCHIVE_PATTERNS:
            if pattern in path_str or path_str.startswith(pattern):
                return True, f"匹配归档模式: {pattern}"

        # 默认保留
        return False, "默认保留"

    def scan_docs(self) -> Tuple[List[Path], List[Path]]:
        """
        扫描docs目录

        Returns:
            (要归档的文件列表, 要保留的文件列表)
        """
        to_archive = []
        to_keep = []

        for file_path in self.docs_dir.rglob("*.md"):
            should_archive, reason = self.should_archive(file_path)

            if should_archive:
                to_archive.append(file_path)
            else:
                to_keep.append(file_path)

        return to_archive, to_keep

    def categorize_files(self, files: List[Path]) -> Dict[str, List[Path]]:
        """分类文件"""
        categories = {
            "fixes": [],
            "tech_reviews": [],
            "troubleshooting": [],
            "analysis": [],
            "blog": [],
            "releases": [],
            "architecture": [],
            "design": [],
            "bugfix": [],
            "summary": [],
            "other": []
        }

        for file_path in files:
            rel_path = file_path.relative_to(self.docs_dir)
            path_str = str(rel_path).lower()

            if "/fixes/" in path_str.replace("\\", "/"):
                categories["fixes"].append(file_path)
            elif "/tech_reviews/" in path_str.replace("\\", "/"):
                categories["tech_reviews"].append(file_path)
            elif "/troubleshooting/" in path_str.replace("\\", "/"):
                categories["troubleshooting"].append(file_path)
            elif "/analysis/" in path_str.replace("\\", "/"):
                categories["analysis"].append(file_path)
            elif "/blog/" in path_str.replace("\\", "/"):
                categories["blog"].append(file_path)
            elif "/releases/" in path_str.replace("\\", "/"):
                categories["releases"].append(file_path)
            elif "/architecture/" in path_str.replace("\\", "/"):
                categories["architecture"].append(file_path)
            elif "/design/" in path_str.replace("\\", "/"):
                categories["design"].append(file_path)
            elif "/bugfix/" in path_str.replace("\\", "/"):
                categories["bugfix"].append(file_path)
            elif "/summary/" in path_str.replace("\\", "/"):
                categories["summary"].append(file_path)
            else:
                categories["other"].append(file_path)

        return categories

    def organize(self):
        """执行整理操作"""
        print("=" * 70)
        print("Documentation Organization Tool")
        print("=" * 70)
        print(f"Docs directory: {self.docs_dir}")
        print(f"Archive directory: {self.archive_dir}")
        print(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'EXECUTE'}")
        print()

        # 扫描文件
        to_archive, to_keep = self.scan_docs()

        # 分类
        categorized = self.categorize_files(to_archive)

        # 显示统计
        print(f"Files to keep: {len(to_keep)}")
        print(f"Files to archive: {len(to_archive)}")
        print()

        # 显示分类详情
        print("Files to archive by category:")
        print("-" * 70)
        for category, files in categorized.items():
            if files:
                print(f"\n{category.upper()} ({len(files)} files):")
                for file_path in files[:5]:  # 只显示前5个
                    rel_path = file_path.relative_to(self.docs_dir)
                    print(f"  - {rel_path}")

                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")

        # 创建归档目录结构
        if not self.dry_run:
            print()
            print("[EXECUTE] Creating archive structure...")
            self.archive_dir.mkdir(exist_ok=True)

            # 创建分类归档目录
            for category in categorized.keys():
                category_dir = self.archive_dir / category
                category_dir.mkdir(exist_ok=True)

            # 移动文件到归档
            print("[EXECUTE] Moving files to archive...")
            archived_count = 0

            for category, files in categorized.items():
                category_dir = self.archive_dir / category
                for file_path in files:
                    try:
                        # 保持相对路径结构
                        rel_path = file_path.relative_to(self.docs_dir)
                        dest_path = category_dir / rel_path.name

                        # 避免文件名冲突
                        counter = 1
                        while dest_path.exists():
                            stem = file_path.stem
                            suffix = file_path.suffix
                            dest_path = category_dir / f"{stem}_{counter}{suffix}"
                            counter += 1

                        shutil.move(str(file_path), str(dest_path))
                        archived_count += 1
                    except Exception as e:
                        print(f"  [ERROR] Failed to archive {file_path}: {e}")

            print()
            print("=" * 70)
            print(f"Archive completed! Archived {archived_count} files")
            print("=" * 70)
        else:
            print()
            print("=" * 70)
            print("DRY RUN completed. To apply changes, run:")
            print("  python scripts/organize_docs.py --execute")
            print("=" * 70)


def main():
    """主函数"""
    import sys

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 检查是否要执行归档
    dry_run = "--execute" not in sys.argv

    # 创建整理器并执行
    organizer = DocOrganizer(project_root, dry_run=dry_run)
    organizer.organize()


if __name__ == "__main__":
    main()
