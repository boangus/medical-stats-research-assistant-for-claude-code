"""Generate Mermaid diagrams from variable lineage.

提供将 MetadataRegistry 中的变量血缘转换为 Mermaid 流程图的工具。
输出可在 Markdown/Obsidian/GitHub 中渲染。

Usage:
    from shared.report_assembler.lineage_mermaid import generate_lineage_mermaid
    diagram = generate_lineage_mermaid(registry, "bmi")
    print(diagram)
"""

from __future__ import annotations

from typing import List, Optional

from shared.metadata_catalog import (
    LineageGraph,
    LineageNode,
    MetadataRegistry,
)


def generate_lineage_mermaid(
    registry: MetadataRegistry,
    variable: Optional[str] = None,
    direction: str = "LR",
) -> str:
    """生成 Mermaid 流程图表示变量血缘。

    Args:
        registry: 元数据目录
        variable: 目标变量名。None 时导出整个图。
        direction: 图方向 (LR/RL/TD/DT)，默认 LR

    Returns:
        Mermaid 文本，可直接嵌入 Markdown 代码块

    Raises:
        VariableNotFoundError: variable 指定但未注册
    """
    if variable is not None:
        graph = registry.lineage(variable)
        nodes, edges = _collect_nodes_edges(graph, registry)
    else:
        nodes, edges = _collect_full_graph(registry)

    lines = [f"graph {direction}"]

    # 节点定义（带描述）
    for node_id, desc in sorted(nodes.items()):
        safe_desc = _escape_label(desc)
        lines.append(f'    {node_id}["{safe_desc}"]')

    # 边定义（源 -> 派生）
    for src, dst in sorted(edges):
        lines.append(f"    {src} --> {dst}")

    return "\n".join(lines)


def _collect_nodes_edges(
    graph: LineageGraph, registry: MetadataRegistry
) -> tuple[dict[str, str], set[tuple[str, str]]]:
    """从 LineageGraph 收集节点和边。"""
    nodes = {}
    edges = set()

    # 目标节点
    target_entry = registry.lookup(graph.variable)
    nodes[graph.variable] = target_entry.description

    # 上游节点 + 边（源 -> 目标）
    for node in graph.upstream:
        nodes[node.variable] = node.entry.description

    # 上游边
    target_sources = target_entry.source_variables
    for src in target_sources:
        if src in nodes:
            edges.add((src, graph.variable))

    # 上游节点之间的边（递归追溯）
    for node in graph.upstream:
        for src in node.entry.source_variables:
            if src in nodes:
                edges.add((src, node.variable))

    # 下游节点 + 边
    for node in graph.downstream:
        nodes[node.variable] = node.entry.description
        # 检查下游节点是否源自当前变量
        if graph.variable in node.entry.source_variables:
            edges.add((graph.variable, node.variable))

    # 下游之间的边
    for node in graph.downstream:
        for src in node.entry.source_variables:
            if src in nodes:
                edges.add((src, node.variable))

    return nodes, edges


def _collect_full_graph(
    registry: MetadataRegistry,
) -> tuple[dict[str, str], set[tuple[str, str]]]:
    """导出整个注册表为图。"""
    nodes = {}
    edges = set()

    for entry in registry.list_all():
        nodes[entry.variable] = entry.description
        for src in entry.source_variables:
            edges.add((src, entry.variable))

    # 补充边的源节点（即使未注册为节点）
    for src, dst in list(edges):
        if src not in nodes:
            nodes[src] = src  # 用变量名作描述

    return nodes, edges


def _escape_label(text: str) -> str:
    """转义 Mermaid 标签中的特殊字符。"""
    return text.replace('"', "'").replace("[", "(").replace("]", ")")
