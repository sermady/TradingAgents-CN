#!/usr/bin/env python3
"""
API文档生成工具

自动生成FastAPI项目的OpenAPI文档和接口文档
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class APIDocGenerator:
    """API文档生成器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.app_dir = project_root / "app"
        self.docs_dir = project_root / "docs" / "api"
        self.openapi_spec = {}

    def extract_router_info(self, router_file: Path) -> Dict[str, Any]:
        """
        提取路由器信息

        Returns:
            路由器信息字典
        """
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取路由信息
            info = {
                "file": router_file.name,
                "endpoints": [],
                "description": ""
            }

            # 简单解析API端点
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('@router.'):
                    # 提取HTTP方法和路径
                    if 'get("' in line or "get('" in line:
                        info["endpoints"].append({"method": "GET", "line": line})
                    elif 'post("' in line or "post('" in line:
                        info["endpoints"].append({"method": "POST", "line": line})
                    elif 'put("' in line or "put('" in line:
                        info["endpoints"].append({"method": "PUT", "line": line})
                    elif 'delete("' in line or "delete('" in line:
                        info["endpoints"].append({"method": "DELETE", "line": line})

            return info

        except Exception as e:
            print(f"Error reading {router_file}: {e}")
            return {}

    def scan_routers(self) -> Dict[str, Any]:
        """扫描所有路由器"""
        routers_dir = self.app_dir / "routers"
        routers = {}

        if not routers_dir.exists():
            print(f"Routers directory not found: {routers_dir}")
            return routers

        for router_file in routers_dir.glob("*.py"):
            if router_file.name.startswith("__"):
                continue

            router_info = self.extract_router_info(router_file)
            if router_info and router_info.get("endpoints"):
                routers[router_file.stem] = router_info

        return routers

    def generate_markdown_doc(self, routers: Dict[str, Any]) -> str:
        """生成Markdown格式的API文档"""
        md_content = []
        md_content.append("# TradingAgents-CN API 文档\n")
        md_content.append("> 自动生成时间: {}\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        md_content.append("\n---\n")

        # 生成目录
        md_content.append("## 目录\n")
        for router_name in sorted(routers.keys()):
            md_content.append(f"- [{router_name}](#{router_name})\n")
        md_content.append("\n---\n")

        # 生成各路由器文档
        for router_name, router_info in sorted(routers.items()):
            md_content.append(f"## {router_name}\n")
            md_content.append(f"**文件**: `app/routers/{router_name}.py`\n")

            if router_info.get("endpoints"):
                md_content.append("\n### API 端点\n\n")

                for endpoint in router_info["endpoints"]:
                    method = endpoint["method"]
                    md_content.append(f"- **{method}**")
                    if endpoint.get("line"):
                        # 简化显示
                        line = endpoint["line"][:80]
                        md_content.append(f" - `{line}`\n")
                    else:
                        md_content.append("\n")

            md_content.append("\n---\n")

        return "".join(md_content)

    def generate(self):
        """生成API文档"""
        print("=" * 70)
        print("API Documentation Generator")
        print("=" * 70)
        print(f"Project root: {self.project_root}")
        print(f"Output directory: {self.docs_dir}")
        print()

        # 创建输出目录
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # 扫描路由器
        print("Scanning routers...")
        routers = self.scan_routers()
        print(f"Found {len(routers)} routers with endpoints")
        print()

        # 显示路由器列表
        print("Routers found:")
        for router_name, router_info in sorted(routers.items()):
            endpoint_count = len(router_info.get("endpoints", []))
            print(f"  - {router_name}: {endpoint_count} endpoints")
        print()

        # 生成Markdown文档
        print("Generating Markdown documentation...")
        md_content = self.generate_markdown_doc(routers)
        md_file = self.docs_dir / "API_REFERENCE.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Generated: {md_file}")
        print()

        # 生成JSON格式的端点列表
        print("Generating JSON endpoint list...")
        endpoints_list = []

        for router_name, router_info in routers.items():
            for endpoint in router_info.get("endpoints", []):
                endpoints_list.append({
                    "router": router_name,
                    "method": endpoint["method"],
                    "file": f"app/routers/{router_name}.py"
                })

        json_file = self.docs_dir / "endpoints.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total": len(endpoints_list),
                "endpoints": endpoints_list
            }, f, indent=2, ensure_ascii=False)

        print(f"Generated: {json_file}")
        print()

        print("=" * 70)
        print("API Documentation Generation Complete!")
        print(f"Total endpoints: {len(endpoints_list)}")
        print(f"Markdown: {md_file}")
        print(f"JSON: {json_file}")
        print("=" * 70)


def main():
    """主函数"""
    from datetime import datetime

    # 获取项目根目录
    project_root = Path(__file__).parent.parent

    # 创建生成器并执行
    generator = APIDocGenerator(project_root)
    generator.generate()


if __name__ == "__main__":
    main()
