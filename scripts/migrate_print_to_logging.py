#!/usr/bin/env python3
"""
migrate_print_to_logging.py — 将 shared/ 下 Python 文件的 print() 迁移为 logging
===============================================================================

迁移策略：
  - 检测文件是否已有 logging 导入，若无则添加
  - 将 print() 替换为 logger.info()
  - 处理 print() 的多参数格式（逗号分隔 → f-string 或 %s 格式）
  - 在 if __name__ == "__main__" 块中添加 logging.basicConfig()

用法：
  python scripts/migrate_print_to_logging.py [--dry-run] [--file FILE]
"""

import re
import sys
from pathlib import Path


def has_logging_import(content: str) -> bool:
    """检查文件是否已导入 logging"""
    return bool(re.search(r"^import logging|^from logging import", content, re.MULTILINE))


def has_logger_defined(content: str) -> bool:
    """检查文件是否已定义 logger"""
    return bool(re.search(r"logger\s*=\s*logging\.getLogger", content))


def add_logging_import(content: str) -> str:
    """在现有 import 块末尾添加 logging 导入和 logger 定义"""
    if has_logging_import(content):
        if not has_logger_defined(content):
            # 在最后一个 import 语句后添加 logger 定义
            lines = content.split("\n")
            last_import_idx = -1
            for i, line in enumerate(lines):
                if re.match(r"^(import |from )", line):
                    last_import_idx = i
            if last_import_idx >= 0:
                lines.insert(last_import_idx + 1, "")
                lines.insert(last_import_idx + 2, "logger = logging.getLogger(__name__)")
                content = "\n".join(lines)
        return content

    # 找到导入块的位置
    lines = content.split("\n")
    last_import_idx = -1
    for i, line in enumerate(lines):
        if re.match(r"^(import |from )", line):
            last_import_idx = i

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, "import logging")
        lines.insert(last_import_idx + 2, "")
        lines.insert(last_import_idx + 3, "logger = logging.getLogger(__name__)")
    else:
        # 文件开头没有 import，在文档字符串后添加
        # 找到文档字符串结束位置
        in_docstring = False
        insert_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring:
                    insert_idx = i + 1
                    break
                elif stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                    insert_idx = i + 1
                    break
                else:
                    in_docstring = True
            elif in_docstring and ('"""' in stripped or "'''" in stripped):
                insert_idx = i + 1
                break

        lines.insert(insert_idx, "import logging")
        lines.insert(insert_idx + 1, "")
        lines.insert(insert_idx + 2, "logger = logging.getLogger(__name__)")
        lines.insert(insert_idx + 3, "")

    return "\n".join(lines)


def add_basicconfig_if_main(content: str) -> str:
    """在 if __name__ == '__main__' 块中添加 logging.basicConfig()"""
    if "logging.basicConfig" in content:
        return content

    # 找到 if __name__ == "__main__" 行
    pattern = r'^(if __name__\s*==\s*["\']__main__["\']\s*:\s*)$'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return content

    # 在该行后插入 basicConfig
    insert_pos = match.end()
    basicconfig = "\n    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')"
    content = content[:insert_pos] + basicconfig + content[insert_pos:]
    return content


def _is_string_literal(s: str) -> bool:
    """检查 s 是否是一个完整的字符串字面量（不含外部运算符）

    正确: "hello", 'hello', f"hello {x}", f'hello'
    错误: "=" * 60, "\n" + "=" * 60, var_name
    """
    s = s.strip()
    if not s:
        return False
    # 去掉可选的 f 前缀
    if s.startswith("f"):
        s = s[1:]
    if len(s) < 2:
        return False
    # 必须以引号开始和结束，且引号匹配
    if s[0] not in ('"', "'"):
        return False
    quote = s[0]
    if s[-1] != quote:
        return False
    # 检查末尾引号是否被转义
    if len(s) > 2 and s[-2] == '\\':
        return False
    return True


def convert_print_args(args_str: str) -> str:
    """将 print() 的参数转换为 logger.info() 的参数格式

    处理情况：
      print("hello") → logger.info("hello")
      print(f"hello {x}") → logger.info(f"hello {x}")
      print("hello", x) → logger.info("hello %s", x)
      print("a", "b", sep=" ") → logger.info("a b")  (简化处理)
      print("=" * 60) → logger.info(str("=" * 60))
    """
    args_str = args_str.strip()
    if not args_str:
        return '""'

    # 简单情况：单个字符串字面量
    if _is_string_literal(args_str):
        return args_str

    # 简单情况：单个变量/表达式（无逗号）
    if "," not in args_str:
        return f'str({args_str})'

    # 多参数情况：检查是否有 sep= 关键字参数
    sep_match = re.search(r',\s*sep\s*=\s*["\'](.+?)["\']', args_str)
    if sep_match:
        sep = sep_match.group(1)
        # 移除 sep 参数
        clean_args = re.sub(r',\s*sep\s*=\s*["\'](.+?)["\']', '', args_str)
        parts = [p.strip() for p in clean_args.split(",")]
        # 构建 f-string
        fmt_parts = []
        for p in parts:
            if _is_string_literal(p):
                fmt_parts.append(p.strip('"').strip("'").lstrip("f"))
            else:
                fmt_parts.append(f"{{{p}}}")
        joined = sep.join(fmt_parts)
        return f'f"{joined}"'

    # 多参数无 sep：用 %s 格式
    parts = [p.strip() for p in args_str.split(",")]
    if len(parts) == 1:
        return parts[0]

    # 第一个参数如果是字符串字面量，用作格式串
    first = parts[0]
    rest = parts[1:]
    if _is_string_literal(first):
        base = first.strip('"').strip("'").lstrip("f")
        placeholders = " ".join(["%s"] * len(rest))
        return f'"{base} {placeholders}", {", ".join(rest)}'
    else:
        # 非字符串第一参数
        placeholders = " ".join(["%s"] * len(parts))
        return f'"{placeholders}", {", ".join(parts)}'


def _find_matching_paren(text: str, start: int) -> int:
    """从 start 位置的 ( 开始，找到匹配的 ) 位置。返回 ) 的索引。"""
    depth = 0
    in_str = None  # 当前字符串引号字符
    escape_next = False
    i = start
    while i < len(text):
        ch = text[i]
        if escape_next:
            escape_next = False
            i += 1
            continue
        if ch == '\\' and in_str:
            escape_next = True
            i += 1
            continue
        if in_str:
            if ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'"):
                in_str = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return -1


def migrate_print_to_logger(content: str) -> str:
    """将文件中的 print() 调用替换为 logger.info()

    使用括号匹配解析器正确处理嵌套括号和字符串
    """
    lines = content.split("\n")
    result_lines = []

    for line in lines:
        # 跳过注释行
        stripped = line.lstrip()
        if stripped.startswith("#"):
            result_lines.append(line)
            continue

        # 检查是否包含 print(
        print_match = re.match(r'^([ \t]*)print\(', line)
        if not print_match:
            result_lines.append(line)
            continue

        prefix = print_match.group(1)
        # print( 的 ( 在行中的位置
        paren_start = len(prefix) + len("print")
        # 找到匹配的 )
        paren_end = _find_matching_paren(line, paren_start)

        if paren_end < 0:
            # 未找到匹配的括号，跳过（可能是多行 print）
            result_lines.append(line)
            continue

        # 提取 print() 内的参数
        args = line[paren_start + 1:paren_end]
        converted = convert_print_args(args)
        result_lines.append(f"{prefix}logger.info({converted})")

    return "\n".join(result_lines)


def migrate_file(filepath: Path, dry_run: bool = False) -> dict:
    """迁移单个文件"""
    original = filepath.read_text(encoding="utf-8")
    content = original

    # 检查是否有 print()
    if "print(" not in content:
        return {"file": str(filepath), "status": "skipped", "reason": "no print() calls"}

    # 统计 print() 数量
    print_count = len(re.findall(r'^[ \t]*print\(', content, re.MULTILINE))

    # 迁移
    content = add_logging_import(content)
    content = migrate_print_to_logger(content)
    content = add_basicconfig_if_main(content)

    if content == original:
        return {"file": str(filepath), "status": "skipped", "reason": "no changes needed"}

    if not dry_run:
        filepath.write_text(content, encoding="utf-8")

    return {
        "file": str(filepath),
        "status": "migrated",
        "print_count": print_count,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migrate print() to logging in shared/ Python files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--file", type=str, help="Migrate a single file")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    if args.file:
        files = [Path(args.file)]
    else:
        files = sorted((project_root / "shared").rglob("*.py"))

    results = {"migrated": [], "skipped": [], "errors": []}

    for f in files:
        try:
            result = migrate_file(f, dry_run=args.dry_run)
            if result["status"] == "migrated":
                results["migrated"].append(result)
            else:
                results["skipped"].append(result)
        except Exception as e:
            results["errors"].append({"file": str(f), "error": str(e)})

    # 输出汇总
    print(f"\n{'=' * 60}")
    print(f"Migration {'Preview' if args.dry_run else 'Complete'}")
    print(f"{'=' * 60}")
    print(f"  Migrated: {len(results['migrated'])} files")
    print(f"  Skipped:  {len(results['skipped'])} files")
    print(f"  Errors:   {len(results['errors'])} files")

    if results["migrated"]:
        total_prints = sum(r.get("print_count", 0) for r in results["migrated"])
        print(f"\n  Total print() calls replaced: {total_prints}")
        print(f"\n  Migrated files:")
        for r in results["migrated"]:
            print(f"    {r['file']} ({r.get('print_count', '?')} calls)")

    if results["errors"]:
        print(f"\n  Errors:")
        for r in results["errors"]:
            print(f"    {r['file']}: {r['error']}")


if __name__ == "__main__":
    main()
