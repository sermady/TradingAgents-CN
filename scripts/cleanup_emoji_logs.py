#!/usr/bin/env python3
"""
清理日志中的Emoji表情符号

将所有日志中的Unicode emoji替换为ASCII字符，提升Windows兼容性
"""

import re
import os
from pathlib import Path
from typing import Dict, Tuple


# Emoji到ASCII的映射表
EMOJI_MAP: Dict[str, str] = {
    # 常用符号
    "🔍": "[SEARCH]",
    "📂": "[DIR]",
    "📄": "[FILE]",
    "💡": "[INFO]",
    "🚀": "[START]",
    "📍": "[LOC]",
    "🔌": "[PORT]",
    "🐛": "[DEBUG]",
    "📚": "[DOCS]",
    "🔧": "[CONFIG]",
    "📊": "[DB]",
    "🔴": "[REDIS]",
    "🔐": "[SECURE]",
    "📝": "[LOG]",
    "🌍": "[ENV]",
    "🔄": "[SYNC]",
    "✅": "[OK]",
    "❌": "[FAIL]",
    "⚠️": "[WARN]",
    "ℹ️": "[INFO]",
    "📋": "[LIST]",
    "🛑": "[STOP]",
    "⏱️": "[TIME]",
    "🔗": "[LINK]",
    "🎯": "[TARGET]",
    "📈": "[UP]",
    "📉": "[DOWN]",
    "🏃": "[RUN]",
    "📦": "[PKG]",
    "🌐": "[WEB]",
    "🎨": "[UI]",
    "💾": "[SAVE]",
    "📤": "[EXPORT]",
    "📥": "[IMPORT]",
    "🔒": "[LOCK]",
    "📣": "[NOTIFY]",
    "📢": "[ANNOUNCE]",
    "🔔": "[BELL]",
    "👤": "[USER]",
    "👥": "[USERS]",
    "⚡": "[FAST]",
    "🔥": "[HOT]",
    "💪": "[STRONG]",
    "🎉": "[SUCCESS]",
    "🌟": "[STAR]",
    "✨": "[SHINE]",
    "🚨": "[ALERT]",
    "⛔": "[BAN]",
    "🔕": "[MUTE]",
    "📻": "[RADIO]",
    "🎵": "[MUSIC]",
    "🎮": "[GAME]",
    "🏆": "[TROPHY]",
    "🥇": "[GOLD]",
    "🥈": "[SILVER]",
    "🥉": "[BRONZE]",
    "🏁": "[FINISH]",
    "🚩": "[FLAG]",
    "🏗️": "[BUILD]",
    "📱": "[MOBILE]",
    "💻": "[PC]",
    "⌨️": "[KEYBOARD]",
    "🖥️": "[MONITOR]",
    "🖨️": "[PRINT]",
    "🖱️": "[MOUSE]",
    "🗜️": "[ZIP]",
    "📁": "[FOLDER]",
    "📂": "[FOLDER-OPEN]",
    "🗂️": "[CARDS]",
    "📅": "[DATE]",
    "📆": "[CALENDAR]",
    "🗓️": "[CALENDAR-2]",
    "📇": "[INDEX]",
    "📈": "[CHART-UP]",
    "📉": "[CHART-DOWN]",
    "📊": "[CHART]",
    "📋": "[CLIPBOARD]",
    "📌": "[PIN]",
    "📍": "[LOC]",
    "📎": "[PAPERCLIP]",
    "🖇️": "[LINKED]",
    "✂️": "[CUT]",
    "📐": "[RULER]",
    "📍": "[LOC]",
    # 数字相关
    "0️⃣": "[0]",
    "1️⃣": "[1]",
    "2️⃣": "[2]",
    "3️⃣": "[3]",
    "4️⃣": "[4]",
    "5️⃣": "[5]",
    "6️⃣": "[6]",
    "7️⃣": "[7]",
    "8️⃣": "[8]",
    "9️⃣": "[9]",
}


class EmojiCleaner:
    """Emoji清理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.files_processed = 0
        self.files_modified = 0
        self.emojis_found = 0

    def clean_file(self, file_path: Path) -> Tuple[bool, int]:
        """
        清理文件中的emoji

        Returns:
            (是否修改, emoji数量)
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            emoji_count = 0

            # 替换所有emoji
            for emoji, replacement in EMOJI_MAP.items():
                count = content.count(emoji)
                if count > 0:
                    content = content.replace(emoji, replacement)
                    emoji_count += count

            # 如果没有修改，返回False
            if content == original_content:
                return False, 0

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, emoji_count

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False, 0

    def scan_directory(self, directory: Path) -> list:
        """扫描目录中的Python文件"""
        python_files = []

        for file_path in directory.rglob("*.py"):
            # 跳过虚拟环境和缓存目录
            if any(skip in file_path.parts for skip in [
                "__pycache__",
                "venv",
                ".venv",
                "env",
                "node_modules",
                ".git"
            ]):
                continue

            python_files.append(file_path)

        return python_files

    def clean_all(self, dry_run: bool = True):
        """清理所有文件中的emoji"""
        print("=" * 70)
        print("Emoji Log Cleaner")
        print("=" * 70)
        print(f"Project root: {self.project_root}")
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'EXECUTE'}")
        print()

        # 扫描Python文件
        print("Scanning Python files...")
        python_files = self.scan_directory(self.project_root / "app")
        python_files.extend(self.scan_directory(self.project_root / "tradingagents"))

        print(f"Found {len(python_files)} Python files to check")
        print()

        # 处理每个文件
        for file_path in python_files:
            self.files_processed += 1

            modified, emoji_count = self.clean_file(file_path)

            if modified:
                self.files_modified += 1
                self.emojis_found += emoji_count
                rel_path = file_path.relative_to(self.project_root)
                print(f"  [MODIFIED] {rel_path} ({emoji_count} emojis)")

        # 打印统计
        print()
        print("=" * 70)
        print("Summary:")
        print(f"  Files processed: {self.files_processed}")
        print(f"  Files modified: {self.files_modified}")
        print(f"  Total emojis replaced: {self.emojis_found}")
        print("=" * 70)

        if dry_run and self.files_modified > 0:
            print()
            print("To apply changes, run:")
            print("  python scripts/cleanup_emoji_logs.py --execute")


def main():
    """主函数"""
    import sys

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 检查是否要执行修改
    dry_run = "--execute" not in sys.argv

    # 创建清理器并执行
    cleaner = EmojiCleaner(project_root)
    cleaner.clean_all(dry_run=dry_run)


if __name__ == "__main__":
    main()
