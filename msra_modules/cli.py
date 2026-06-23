#!/usr/bin/env python
"""
MSRA Modules CLI - 实验性模块管理工具
"""

import argparse
import sys
from . import (
    list_modules,
    check_module_dependencies,
    get_module_status,
)


def print_module_info(module_name: str = None):
    """打印模块信息"""
    modules = list_modules()

    if module_name:
        if module_name not in modules:
            print(f"❌ 模块 {module_name} 不存在")
            sys.exit(1)

        info = modules[module_name]
        deps = check_module_dependencies(module_name)
        print(f"\n{'='*50}")
        print(f"模块: {module_name}")
        print(f"{'='*50}")
        print(f"描述: {info['description']}")
        print(f"状态: {info['status']}")
        print(f"\n功能:")
        for cap in info["capabilities"]:
            print(f"  ✓ {cap}")
        print(f"\n依赖:")
        for dep, installed in deps["dependencies_installed"].items():
            status = "✅" if installed else "❌"
            print(f"  {status} {dep}")
        if deps["all_installed"]:
            print(f"\n✅ 所有依赖已安装，模块可用")
        else:
            print(f"\n⚠️ 部分依赖未安装，模块可能无法正常使用")
            print(f"   安装命令: pip install 'medical-stats-research-assistant[{module_name}]'")
    else:
        print(f"\n{'='*50}")
        print(f"MSRA 实验性模块列表")
        print(f"{'='*50}")
        for name, info in modules.items():
            status = get_module_status(name)
            deps = check_module_dependencies(name)
            all_installed = deps["all_installed"]
            status_icon = "✅" if all_installed else "⚠️"
            print(f"\n{status_icon} {name}")
            print(f"   描述: {info['description']}")
            print(f"   状态: {status}")
            print(f"   功能: {', '.join(info['capabilities'][:3])}{'...' if len(info['capabilities']) > 3 else ''}")


def main():
    parser = argparse.ArgumentParser(
        prog="msra-modules",
        description="MSRA 实验性模块管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  msra-modules list           # 列出所有模块
  msra-modules info imaging   # 查看医学影像模块详情
  msra-modules check bioinformatics  # 检查生物信息模块依赖
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    list_parser = subparsers.add_parser("list", help="列出所有模块")

    info_parser = subparsers.add_parser("info", help="查看模块详情")
    info_parser.add_argument("module", nargs="?", help="模块名称")

    check_parser = subparsers.add_parser("check", help="检查模块依赖")
    check_parser.add_argument("module", help="模块名称")

    args = parser.parse_args()

    if args.command == "list":
        print_module_info()
    elif args.command == "info":
        print_module_info(args.module)
    elif args.command == "check":
        deps = check_module_dependencies(args.module)
        if "error" in deps:
            print(f"❌ {deps['error']}")
            sys.exit(1)
        print(f"\n依赖检查结果: {args.module}")
        print("-" * 40)
        for dep, installed in deps["dependencies_installed"].items():
            status = "✅ 已安装" if installed else "❌ 未安装"
            print(f"  {dep}: {status}")
        if deps["all_installed"]:
            print("\n✅ 所有依赖已安装")
            sys.exit(0)
        else:
            print(f"\n⚠️ 部分依赖未安装")
            print(f"   安装命令: pip install 'medical-stats-research-assistant[{args.module}]'")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
