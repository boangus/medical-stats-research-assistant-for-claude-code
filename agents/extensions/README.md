# External Resources Registry - 外部资源注册表

> 本目录整合和管理与MSRA项目相关的外部开源资源和学术文献。

## 目录结构

```
agents/extensions/
├── README.md                           # 本文件 - 资源目录总览
├── registry/                           # 资源注册表
│   ├── github_projects.json            # GitHub开源项目注册
│   ├── academic_literature.json       # 学术文献注册
│   └── integration_status.json        # 集成状态追踪
├── github/                            # GitHub资源详情
│   ├── causal_inference/               # 因果推断类
│   ├── survival_analysis/              # 生存分析类
│   ├── meta_analysis/                  # Meta分析类
│   ├── propensity_score/               # 倾向性评分类
│   ├── missing_data/                   # 缺失数据类
│   ├── visualization/                  # 可视化类
│   └── reporting/                      # 报告规范类
├── academic/                          # 学术文献详情
│   ├── methods/                       # 方法学研究
│   ├── best_practices/                 # 最佳实践
│   └── trends/                        # 前沿趋势
├── integration/                       # 集成工具
│   ├── resource_loader.py              # 资源加载器
│   ├── compatibility_checker.py        # 兼容性检查器
│   └── update_tracker.py              # 更新追踪器
├── optimization/                       # 持续优化
│   ├── scan_scheduler.py               # 扫描调度器
│   ├── quality_metrics.py              # 质量指标
│   └── improvement_tracker.py          # 改进追踪
└── tests/                            # 资源相关测试
    ├── test_resource_loader.py
    ├── test_compatibility.py
    └── test_integration.py
```

## 使用说明

### 1. 添加新资源

编辑 `registry/github_projects.json` 或 `registry/academic_literature.json`，
按格式添加新资源条目。

### 2. 检查集成状态

运行 `python -m agents.extensions.integration.check_status` 查看各资源的集成状态。

### 3. 运行优化扫描

```bash
# 全面扫描
python -m agents.extensions.optimization.full_scan

# 快速检查更新
python -m agents.extensions.optimization.quick_check
```

### 4. 运行测试

```bash
pytest agents/extensions/tests/ -v
```

## 维护规范

- 每月进行资源更新扫描
- 每季度进行兼容性评估
- 每次重要更新后运行完整测试套件
- 更新需记录在 CHANGELOG.md

## 许可证说明

各外部资源的许可证以其各自的许可证为准。本目录仅作整合和管理之用。
