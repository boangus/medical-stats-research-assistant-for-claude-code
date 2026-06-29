#!/usr/bin/env python3
"""
MSRA Variable DAG Template — 变量依赖关系 DAG 生成器

在 analysis-plan Phase 6.5 自动调用，从 SAP Section 7 变量构造定义中
提取变量依赖关系，生成有向无环图（DAG）可视化。

Usage:
    from variable_dag_template import generate_variable_dag
    dag_path = generate_variable_dag(sap_path, output_dir="MSRA/reports/figures")
"""

import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)


def parse_variable_constructions(sap_path: str) -> list[dict]:
    """
    从 SAP 文件中解析 Section 7.6 变量构造定义表。

    Args:
        sap_path: SAP 文件路径

    Returns:
        变量构造定义列表，每项包含 variable, type, formula, dependencies
    """
    if not os.path.exists(sap_path):
        return []

    with open(sap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 定位 Section 7.6 变量构造定义
    section_match = re.search(
        r"## 7\.6\s+变量构造定义\s*\n(.+?)(?=\n## [89]|\n## \d|\Z)",
        content, re.DOTALL
    )
    if not section_match:
        return []

    section = section_match.group(1)

    # 解析 Markdown 表格行
    variables = []
    for line in section.split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 3:
            continue
        # 跳过表头
        if cells[0] in ("变量名", "变量", "---", "--------"):
            continue

        var_name = cells[0]
        var_type = cells[1] if len(cells) > 1 else "未知"
        formula = cells[2] if len(cells) > 2 else ""

        # 从公式中提取依赖变量
        deps = _extract_dependencies(var_name, formula)

        variables.append({
            "variable": var_name,
            "type": var_type,
            "formula": formula,
            "dependencies": deps,
        })

    return variables


def _extract_dependencies(target_var: str, formula: str) -> list[str]:
    """
    从构造公式中提取源变量名。

    策略：
    - 排除目标变量自身
    - 排除数字、运算符、中文、常见函数名
    - 提取英文标识符作为变量引用
    """
    if not formula or formula.strip() in ("-", "N/A", ""):
        return []

    # 已知非变量 token（常见函数/关键字）
    stop_words = {
        "and", "or", "not", "if", "then", "else", "none", "null",
        "nan", "true", "false", "min", "max", "mean", "sum", "abs",
        "sqrt", "log", "exp", "round", "int", "float", "str",
        "kg", "cm", "mm", "ml", "mg", "dl", "unit", "units",
        "vs", "versus", "recist", "who", "charlson", "index",
    }

    # 提取英文标识符（2+ 字符）
    tokens = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", formula)
    deps = []
    seen = set()
    for t in tokens:
        t_lower = t.lower()
        if t_lower == target_var.lower():
            continue
        if t_lower in stop_words:
            continue
        if len(t) < 2:
            continue
        if t_lower not in seen:
            seen.add(t_lower)
            deps.append(t)

    return deps


def classify_variables(variables: list[dict]) -> dict:
    """
    将变量分类为原始变量和衍生变量。

    Returns:
        {"original": [...], "derived": [...]}
    """
    derived_names = {v["variable"].lower() for v in variables}
    all_dep_names = set()
    for v in variables:
        for dep in v["dependencies"]:
            all_dep_names.add(dep.lower())

    # 衍生变量：有构造公式的变量
    derived = [v for v in variables if v["dependencies"] or (
        v["formula"] and v["formula"].strip() not in ("-", "", "N/A")
    )]

    # 原始变量：被依赖但自身不在构造表中的变量
    derived_var_names = {v["variable"].lower() for v in derived}
    original = []
    for dep_name in all_dep_names:
        if dep_name not in derived_var_names:
            original.append({"variable": dep_name, "type": "原始变量", "formula": "", "dependencies": []})

    return {"original": original, "derived": derived}


def generate_dot(variables: list[dict]) -> str:
    """
    生成 Graphviz DOT 格式的 DAG 定义。

    Args:
        variables: 变量构造定义列表

    Returns:
        DOT 格式字符串
    """
    classified = classify_variables(variables)
    original = classified["original"]
    derived = classified["derived"]

    # 收集所有节点
    original_names = {v["variable"].lower() for v in original}
    derived_names = {v["variable"] for v in derived}

    lines = []
    lines.append("digraph VariableDAG {")
    lines.append("    rankdir=LR;")
    lines.append('    node [fontname="SimHei,Arial"];')
    lines.append('    edge [fontname="Arial"];')
    lines.append("")

    # 原始变量节点（圆形，浅蓝）
    lines.append("    // 原始变量")
    for v in original:
        name = v["variable"]
        lines.append(f'    "{name}" [shape=circle, style=filled, fillcolor="#E3F2FD", label="{name}"];')

    # 衍生变量节点（方形，浅橙）
    lines.append("")
    lines.append("    // 衍生变量")
    for v in derived:
        name = v["variable"]
        var_type = v.get("type", "")
        label = f"{name}\\n({var_type})" if var_type else name
        lines.append(f'    "{name}" [shape=box, style=filled, fillcolor="#FFF3E0", label="{label}"];')

    # 边（依赖关系）
    lines.append("")
    lines.append("    // 依赖关系")
    for v in derived:
        for dep in v["dependencies"]:
            lines.append(f'    "{dep}" -> "{v["variable"]}";')

    lines.append("}")
    return "\n".join(lines)


def generate_ascii_dag(variables: list[dict]) -> str:
    """
    生成 ASCII 文本格式的 DAG（graphviz 不可用时的降级方案）。

    Args:
        variables: 变量构造定义列表

    Returns:
        ASCII DAG 字符串
    """
    classified = classify_variables(variables)
    derived = classified["derived"]

    lines = []
    lines.append("变量依赖关系图（ASCII）")
    lines.append("=" * 50)

    if not derived:
        lines.append("（无衍生变量，所有变量为原始变量）")
        return "\n".join(lines)

    for v in derived:
        name = v["variable"]
        deps = v["dependencies"]
        if deps:
            dep_str = " + ".join(deps)
            lines.append(f"  {dep_str} ──→ {name}")
        else:
            lines.append(f"  (独立) ──→ {name}")

    lines.append("")
    lines.append("图例: ○ 原始变量  □ 衍生变量")
    return "\n".join(lines)


def generate_variable_dag(
    sap_path: str,
    output_dir: Optional[str] = None,
) -> str:
    """
    从 SAP 中提取变量依赖关系并生成 DAG。

    Args:
        sap_path: SAP 文件路径
        output_dir: 输出目录（可选，生成 PNG）

    Returns:
        DAG 描述文本（DOT 或 ASCII）
    """
    variables = parse_variable_constructions(sap_path)

    if not variables:
        return "[无法解析变量构造定义 — SAP Section 7.6 不存在或为空]"

    # 尝试生成 graphviz PNG
    if output_dir:
        try:
            dot_text = generate_dot(variables)
            _render_png(dot_text, output_dir)
        except Exception:
            pass  # graphviz 不可用时不阻断

    # 返回文本表示
    try:
        import shutil
        if shutil.which("dot"):
            return generate_dot(variables)
    except Exception:
        pass

    return generate_ascii_dag(variables)


def _render_png(dot_text: str, output_dir: str):
    """使用 graphviz 渲染 PNG"""
    import subprocess
    import tempfile

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "variable_dag.png")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False, encoding="utf-8") as f:
        f.write(dot_text)
        dot_path = f.name

    try:
        subprocess.run(
            ["dot", "-Tpng", "-o", output_path, dot_path],
            check=True, capture_output=True, timeout=30
        )
    finally:
        os.unlink(dot_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    import sys

    if len(sys.argv) < 2:
        logger.info("Usage: python variable_dag_template.py <sap_path> [output_dir]")
        sys.exit(1)

    sap = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    result = generate_variable_dag(sap, output_dir=out)
    logger.info("result")
