# 表格与图表理解方法融合方案

> 项目：medical-stats-research-assistant
> 目标：将先进的表格和图表理解方法融入现有插件，提升表格核查和图表理解能力
> 创建时间：2026-06-18
> 状态：进行中

---

## 一、总体目标

将以下表格和图表理解方法融入现有插件：

### 表格理解方法
1. **Chain-of-Table**：逐步构建和验证表格，提升复杂表格的理解能力
2. **Tree-of-Table**：将大表格层次化分解为树状结构，便于LLM推理
3. **TableMaster**：提取和语义化表格内容，在文本和符号推理间自适应切换

### 图表理解方法
1. **FDV（Formalized Description for Visualization）**：将图表转化为结构化文本描述，支持多样化和更深入的理解

---

## 二、实施计划

### 阶段1：基础架构搭建（预计1-2天）

#### 任务1.1：创建表格理解模块目录结构
- **目标**：建立`shared/table-understanding/`目录及基础文件
- **状态**：未开始
- **备注**：

#### 任务1.2：创建图表理解模块目录结构
- **目标**：建立`shared/chart-understanding/`目录及基础文件
- **状态**：未开始
- **备注**：

#### 任务1.3：更新现有模块接口
- **目标**：修改`shared/report-assembler/compliance_checker.py`和`render_report_html.py`，添加表格和图表理解接口
- **状态**：未开始
- **备注**：

### 阶段2：表格理解方法实现（预计2-3天）

#### 任务2.1：实现Chain-of-Table核查器
- **目标**：创建`shared/table-understanding/table_chain_verifier.py`
- **功能**：
  - 解析表格结构
  - 逐步验证数据一致性
  - 检查逻辑关系
  - 生成核查报告
- **状态**：未开始
- **备注**：

#### 任务2.2：实现Tree-of-Table分析器
- **目标**：创建`shared/table-understanding/table_tree_analyzer.py`
- **功能**：
  - 构建表格的树状结构
  - 分析表格层次关系
  - 支持复杂表格的层次化理解
- **状态**：未开始
- **备注**：

#### 任务2.3：实现TableMaster提取器
- **目标**：创建`shared/table-understanding/table_master_extractor.py`
- **功能**：
  - 提取表格关键信息
  - 语义化表格内容
  - 在文本和符号推理间自适应切换
- **状态**：未开始
- **备注**：

### 阶段3：图表理解方法实现（预计1-2天）

#### 任务3.1：实现FDV描述生成器
- **目标**：创建`shared/chart-understanding/chart_fdv_generator.py`
- **功能**：
  - 提取图表数据点
  - 描述坐标轴信息
  - 提取关键发现
  - 生成统计摘要
- **状态**：未开始
- **备注**：

### 阶段4：集成到现有流水线（预计1-2天）

#### 任务4.1：更新质量检查模块
- **目标**：修改`shared/report-assembler/compliance_checker.py`
- **新增检查项**：
  - 表格结构完整性检查
  - 表格数据一致性检查
  - 图表与文本一致性检查
  - 图表质量自动化评估
- **状态**：未开始
- **备注**：

#### 任务4.2：更新报告生成模块
- **目标**：修改`shared/report-assembler/render_report_html.py`
- **新增功能**：
  - 表格语义化描述生成
  - 图表结构化描述生成
  - 表格和图表的自动化核查报告
- **状态**：未开始
- **备注**：

### 阶段5：测试与验证（预计1天）

#### 任务5.1：创建单元测试
- **目标**：为新功能创建测试用例
- **测试文件**：
  - `tests/test_table_understanding.py`
  - `tests/test_chart_understanding.py`
- **状态**：未开始
- **备注**：

#### 任务5.2：使用现有数据验证
- **目标**：使用现有测试数据验证新功能
- **测试数据**：`tests/msra_test_data.csv`
- **状态**：未开始
- **备注**：

### 阶段6：文档与同步（预计0.5天）

#### 任务6.1：更新文档
- **目标**：更新README.md和相关文档
- **内容**：
  - 新增功能说明
  - 使用示例
  - API文档
- **状态**：未开始
- **备注**：

#### 任务6.2：同步到GitHub
- **目标**：提交所有更改并推送到GitHub
- **操作**：
  - git add .
  - git commit -m "feat: 集成表格和图表理解方法"
  - git push origin main
- **状态**：未开始
- **备注**：

---

## 三、技术细节

### 3.1 表格理解模块接口设计

```python
# shared/table-understanding/__init__.py
from .table_chain_verifier import TableChainVerifier
from .table_tree_analyzer import TableTreeAnalyzer
from .table_master_extractor import TableMasterExtractor

__all__ = ['TableChainVerifier', 'TableTreeAnalyzer', 'TableMasterExtractor']
```

### 3.2 图表理解模块接口设计

```python
# shared/chart-understanding/__init__.py
from .chart_fdv_generator import ChartFDVGenerator

__all__ = ['ChartFDVGenerator']
```

### 3.3 质量检查集成示例

```python
# shared/report-assembler/compliance_checker.py 新增函数
def check_table_understanding(table_data):
    """检查表格理解质量"""
    from ..table_understanding import TableChainVerifier, TableTreeAnalyzer
    
    verifier = TableChainVerifier(table_data)
    chain_results = verifier.verify()
    
    analyzer = TableTreeAnalyzer(table_data)
    tree_analysis = analyzer.analyze()
    
    return {
        'chain_verification': chain_results,
        'tree_analysis': tree_analysis
    }
```

---

## 四、进度跟踪

| 任务ID | 任务名称 | 状态 | 完成时间 | 备注 |
|--------|----------|------|----------|------|
| 1.1 | 创建表格理解模块目录结构 | 未开始 | - | - |
| 1.2 | 创建图表理解模块目录结构 | 未开始 | - | - |
| 1.3 | 更新现有模块接口 | 未开始 | - | - |
| 2.1 | 实现Chain-of-Table核查器 | 未开始 | - | - |
| 2.2 | 实现Tree-of-Table分析器 | 未开始 | - | - |
| 2.3 | 实现TableMaster提取器 | 未开始 | - | - |
| 3.1 | 实现FDV描述生成器 | 未开始 | - | - |
| 4.1 | 更新质量检查模块 | 未开始 | - | - |
| 4.2 | 更新报告生成模块 | 未开始 | - | - |
| 5.1 | 创建单元测试 | 未开始 | - | - |
| 5.2 | 使用现有数据验证 | 未开始 | - | - |
| 6.1 | 更新文档 | 未开始 | - | - |
| 6.2 | 同步到GitHub | 未开始 | - | - |

---

## 五、风险评估

### 5.1 技术风险
- **风险**：新方法可能与现有代码不兼容
- **缓解**：采用模块化设计，提供清晰的API接口

### 5.2 时间风险
- **风险**：实施时间可能超出预期
- **缓解**：分阶段实施，优先实现核心功能

### 5.3 质量风险
- **风险**：新功能可能存在bug
- **缓解**：创建全面的单元测试，使用现有数据验证

---

## 六、成功标准

1. **功能完整性**：所有计划功能都已实现
2. **代码质量**：通过所有单元测试，无语法错误
3. **文档完整性**：所有新功能都有文档说明
4. **同步成功**：所有更改已成功推送到GitHub

---

## 七、更新日志

### 2026-06-18
- 创建融合方案文档
- 开始实施阶段1

---

*文档最后更新：2026-06-18*