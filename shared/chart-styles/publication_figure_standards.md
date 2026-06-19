# 发表级图表标准

> MSRA 项目专用。定义结果阶段输出给用户的图表必须达到的发表级标准。
> 参考：nature-skills/nature-figure（Nature 期刊图表工作流）的设计理论和 API 规范。
> 适用范围：analysis-exec Phase 9 输出图表、report Phase 4 生成图表。
>
> 关联文件：
> - shared/chart-styles/font_and_size_specs.json — 期刊字体与尺寸规格
> - shared/chart-styles/journal_color_schemes.json — 期刊配色方案
> - shared/chart-styles/chart_types.json — 图表类型规范
> - shared/chart-styles/variable_naming_conventions.md — 变量命名规范
> - shared/templates/publication_figure_template.py — 发表级图表 Python 模板

---

## 设计初衷

医学统计研究的图表是结果传达的核心载体。发表级图表不仅要求美观，更要求：

1. **科学严谨**：数据展示无误导，坐标轴/比例尺/误差线准确
2. **期刊合规**：符合目标期刊的字体、尺寸、分辨率、配色要求
3. **信息高效**：多面板图表遵循信息层级，无冗余面板
4. **变量规范**：所有变量名称统一、规范、含单位
5. **可编辑性**：输出矢量格式（SVG），文本可编辑

---

## 一、强制 rcParams 配置

> **IRON RULE**：以下三行 rcParams 必须出现在每个绘图脚本的最前面，无例外。
> 来源：nature-skills/nature-figure 强制规则。

```python
import matplotlib.pyplot as plt

# ── 强制配置：保证 SVG 文本可编辑 ──────────────────────────────────
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'   # 文本保持为 <text> 节点，非路径
```

**为什么 `svg.fonttype = 'none'`**：matplotlib 默认值 `'path'` 会将每个字符转换为贝塞尔路径，
导致文本不可选中、不可搜索、无法在 Illustrator/Inkscape 中重新对齐。设置为 `'none'` 后，
文本保持为 SVG `<text>` 元素，字体替换在渲染时发生。

### 完整发表级样式函数

```python
def apply_publication_style(font_size=8, axes_linewidth=1.0, use_tex=False):
    """
    应用发表级 rcParams。在创建任何图表前调用一次。

    Parameters
    ----------
    font_size : int
        基础字号。发表级密集多面板：7-9pt；大型对比柱状图：24pt；紧凑子图：15-16pt
    axes_linewidth : float
        坐标轴线宽。发表级：0.8-1.2；大型面板：3.0
    use_tex : bool
        是否使用 LaTeX 渲染数学标签（需安装 LaTeX）
    """
    # ── 强制：可编辑 SVG 文本 ──────────────────────────────────────
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['svg.fonttype'] = 'none'

    # ── 布局与样式 ────────────────────────────────────────────────
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.spines.right'] = False    # 右侧轴线关闭
    plt.rcParams['axes.spines.top'] = False      # 顶部轴线关闭
    plt.rcParams['axes.linewidth'] = axes_linewidth
    plt.rcParams['legend.frameon'] = False       # 无边框图例

    # ── 中文字体支持 ──────────────────────────────────────────────
    plt.rcParams['font.sans-serif'] = ['Arial', 'Noto Sans CJK SC', 'DejaVu Sans', 'sans-serif']

    if use_tex:
        plt.rcParams['text.usetex'] = True
```

### 预设方案

| 场景 | 调用方式 | 适用 |
|------|---------|------|
| 发表级密集多面板 | `apply_publication_style(font_size=8, axes_linewidth=1)` | Nature/Lancet 双栏图 |
| 标准医学图表 | `apply_publication_style(font_size=10, axes_linewidth=1.2)` | KM曲线/森林图/ROC |
| 大型对比柱状图 | `apply_publication_style(font_size=24, axes_linewidth=3)` | 多方法对比 |
| 紧凑子图 | `apply_publication_style(font_size=15, axes_linewidth=2)` | 补充材料图 |

---

## 二、配色方案

### 2.1 语义化调色板

> 来源：nature-skills/nature-figure 语义配色系统。
> 蓝色 = 主要方法/治疗组，绿色 = 阳性/改善，红色 = 基线/对照，中性色 = 参考/背景。

```python
PALETTE = {
    # 主要方法 / 治疗组
    "blue_main":      "#0F4D92",   # 深蓝 — 核心方法
    "blue_secondary": "#3775BA",   # 中蓝 — 次要方法
    # 阳性 / 改善色阶（浅→深）
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",
    # 基线 / 对照色阶（浅→深）
    "red_1":      "#F6CFCB",
    "red_2":      "#E9A6A1",
    "red_strong": "#B64342",
    # 中性支持色
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",
    # 强调 / 标注（少量使用）
    "gold":   "#FFD700",
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}

DEFAULT_COLOR_ORDER = [
    "#0F4D92",   # blue_main
    "#8BCF8B",   # green_3
    "#B64342",   # red_strong
    "#42949E",   # teal
    "#9A4D8E",   # violet
    "#CFCECE",   # neutral_light
]
```

### 2.2 色盲安全配色

> 用于需要色盲安全的场景（如投稿期刊要求）。

```python
COLOR_BLIND_SAFE = [
    "#0072B2",  # 蓝
    "#E69F00",  # 橙
    "#009E73",  # 绿
    "#F0E442",  # 黄
    "#56B4E9",  # 浅蓝
    "#D55E00",  # 朱红
    "#CC79A7",  # 粉
]
```

### 2.3 期刊配色映射

与 `shared/chart-styles/journal_color_schemes.json` 集成：

| 期刊 | 主色 | 辅色 | 配色方案键名 |
|------|------|------|------------|
| NEJM | `#1f77b4` (蓝) | `#ff7f0e` (橙) | `NEJM_blue` |
| JAMA | `#c00000` (红) | `#0066cc` (蓝) | `JAMA_red` |
| Lancet | `#00573f` (绿) | `#ff4500` (橙红) | `Lancet_green` |
| BMJ | `#003366` (深蓝) | `#ff6600` (橙) | `BMJ_blue` |
| 中华医学杂志 | `#cc0000` (红) | `#003366` (深蓝) | `CMJ_red` |

### 2.4 配色规则

1. 同一方法/组别在所有面板中使用相同颜色，不得跨面板重新映射
2. 相关基线方法使用同一冷色系，核心方法使用同一暖色系
3. 绿色/红色保留给方向性标注（增加/减少、阳性/阴性）
4. 不确定时降低饱和度而非增加类别数
5. 消融实验使用同一颜色的不同透明度（alpha 0.2→1.0）

---

## 三、多面板信息层级

> **IRON RULE**：多面板图表中，每个面板必须回答一个独特的科学问题。
> 遮住任一面板，其他面板无法弥补其信息缺口。

### 3.1 三级信息递进

| 层级 | 回答的问题 | 典型编码方式 | 医学统计示例 |
|------|----------|------------|------------|
| 概览 | "整体情况如何？" | 堆叠柱状图、组成图 | 基线特征分布 |
| 偏差 | "各组有什么独特之处？" | Z-score 热图（发散色图） | 组间标准化差异 |
| 关系 | "变量间如何共变？" | 散点图/气泡图 | 效应量与协变量关系 |

### 3.2 反冗余检查清单

图表定稿前必须确认：

- [ ] 面板 b 不以不同视觉形式重复展示面板 a 的同一数据
- [ ] 面板 c 增加了 a 和 b 都没有的维度（如相关性、生物关系）
- [ ] 每个面板有自己的坐标轴标签词汇（不同的 x/y 量）

### 3.3 常见冗余陷阱

| 陷阱 | 示例 | 修复 |
|------|------|------|
| 绝对值+绝对值 | 堆叠柱状图(%) + 同一%的热图 | 将热图替换为 Z-score 偏差图 |
| 父集子集 | 仅肿瘤排名柱状图是堆叠柱的一列 | 替换为散点图：肿瘤% vs 免疫% |
| 双排名 | 两个相关指标的排名柱状图 | 将一个替换为散点/气泡图 |
| 不同图同一数据 | 饼图 + 堆叠柱状图 | 合并或替换为关系图 |

---

## 四、图表类型规范

### 4.1 医学统计核心图表

| 图表类型 | 适用场景 | 必需元素 | 推荐尺寸(英寸) |
|---------|---------|---------|---------------|
| KM 生存曲线 | 生存分析 | 删失标记、风险人数表、CI、P值、样本量 | 7×5 |
| 森林图 | 回归/亚组/荟萃 | 效应量、CI、参考线、异质性统计、权重 | 7×4 |
| ROC 曲线 | 诊断试验/预测模型 | TPR/FPR、参考线、AUC+CI、最优截断 | 5×5 |
| 校准曲线 | 预测模型 | 预测/观测概率、参考线、Brier Score | 5×5 |
| 决策曲线 | 临床决策分析 | 阈值概率轴、净获益轴、全治/不治线 | 7×4 |
| 箱线图 | 连续变量分布 | 中位数、四分位、须、异常值点 | 6×4 |
| 柱状图 | 分组比较 | 柱高、误差线、组标签、样本量 | 7×4 |
| 散点图 | 相关性/回归 | 数据点、趋势线、相关系数、CI | 5×5 |
| 热图 | 多变量/相关性 | 色条、行列标签、单元格注释 | 6×5 |
| RCS 曲线 | 非线性关系 | 节点位置、非线性检验P值、参考线 | 6×4 |

### 4.2 图表元素规范

**坐标轴**：
- 仅保留左+下轴线，关闭右+上轴线
- 默认无网格线；如需引导视线，使用稀疏虚线
- Y 轴范围收紧到数据范围，不固定 0-100
- 坐标轴标签必须含变量名和单位（如"收缩压 (mmHg)"）

**误差线**：
- 柱状图：误差线宽度 = 柱宽的 1/3，capsize = 5-10
- 误差线样式：`elinewidth=2, capthick=2, capsize=10`

**图例**：
- 默认无边框（`frameon=False`）
- 多面板图使用共享图例条，置于面板上方
- 空间允许时优先使用直接标注

**面板标签**：
- 小写粗体字母（a, b, c...），置于面板左上角
- 暗色背景面板使用白色标签

**P 值标注**：
- 图表中 P 值格式遵循 `statistical_constraints.md` P-R01~R07
- 显著性标注线连接比较组，线上方标注精确 P 值
- 禁止仅用星号标注，必须同时给出精确 P 值

---

## 五、导出规范

### 5.1 导出格式优先级

> **IRON RULE**：SVG 为首要输出格式，PNG 为次要预览格式。

```python
import os
from pathlib import Path

def export_figure(fig, out_path, formats=None, dpi=300, pad=2, close=True):
    """
    发表级图表导出。

    Parameters
    ----------
    out_path : str
        输出路径（不含扩展名，或含扩展名）
    formats : list
        导出格式列表。默认 ['svg', 'png']
    dpi : int
        PNG 分辨率。标准 300，密集柱状图 600
    pad : float
        tight_layout 间距。默认 2，紧凑多面板 1
    """
    if formats is None:
        formats = ['svg', 'png']

    fig.tight_layout(pad=pad)
    base = Path(out_path)
    if base.suffix:
        base = base.with_suffix('')

    os.makedirs(base.parent, exist_ok=True)
    saved = []
    for fmt in formats:
        p = str(base) + f'.{fmt}'
        fig.savefig(p, dpi=dpi, bbox_inches='tight', format=fmt)
        saved.append(p)

    if close:
        plt.close(fig)

    return saved
```

### 5.2 DPI 指南

| 用途 | DPI | 格式 |
|------|-----|------|
| 标准发表 | 300 | SVG (首要) + PNG (预览) |
| 密集柱状图/多方法对比 | 600 | SVG + PNG |
| 投稿系统上传 | 300 | PNG/TIFF |
| 补充材料 | 150 | PNG |

### 5.3 期刊尺寸规范

与 `shared/chart-styles/font_and_size_specs.json` 集成：

| 期刊 | 单栏宽度(mm) | 双栏宽度(mm) | 最大高度(mm) | DPI |
|------|------------|------------|------------|-----|
| NEJM | 85 | 175 | 230 | 300 |
| JAMA | 85 | 175 | 230 | 300 |
| Lancet | 85 | 175 | 230 | 300 |
| BMJ | 85 | 175 | 230 | 300 |
| 中华医学杂志 | 80 | 160 | 200 | 300 |

---

## 六、变量命名规范集成

> 详细规范参见 `shared/chart-styles/variable_naming_conventions.md`。
> 此处仅列出图表中的关键规则。

### 6.1 图表中的变量展示规则

| 规则 | 内容 | 示例 |
|------|------|------|
| 坐标轴标签 | 变量名 + (单位) | `收缩压 (mmHg)`、`BMI (kg/m²)` |
| 图例标签 | 规范变量名 | `治疗组`、`对照组`（非"group1"、"group2"） |
| 面板标题 | 简洁描述性标题 | `A组 vs B组总生存率`（非"Analysis 1"） |
| 表注/图注 | 变量缩写全称 | `HR: 风险比; CI: 置信区间` |
| P 值标注 | 遵循 P-R01~R07 | `P = 0.003`、`P < 0.001` |

### 6.2 变量名一致性检查

图表中的变量名必须与以下位置完全一致：
- SAP 中的变量定义
- Table 1 中的变量名
- 结果表中的变量名
- 方法学描述中的变量名
- 正文中解读的变量名

---

## 七、质量检查清单

图表输出前必须逐项确认：

```
发表级图表质量检查清单
├── 强制配置
│   ├── [ ] font.family = 'sans-serif'
│   ├── [ ] font.sans-serif 包含 'Arial'
│   ├── [ ] svg.fonttype = 'none'
│   ├── [ ] axes.spines.right = False
│   └── [ ] axes.spines.top = False
├── 配色
│   ├── [ ] 使用语义化调色板（PALETTE 或期刊配色）
│   ├── [ ] 同一方法/组别跨面板颜色一致
│   ├── [ ] 色盲安全（如期刊要求）
│   └── [ ] 无纯红/纯绿/纯蓝原色
├── 信息层级
│   ├── [ ] 每个面板回答独特科学问题
│   ├── [ ] 无冗余面板（反冗余检查通过）
│   └── [ ] 面板标签 a/b/c 已添加
├── 数据展示
│   ├── [ ] 坐标轴含变量名和单位
│   ├── [ ] Y轴范围收紧到数据范围
│   ├── [ ] 误差线正确（SD/SE/CI 已标注）
│   ├── [ ] P值格式符合 P-R01~R07
│   └── [ ] 样本量已标注
├── 变量命名
│   ├── [ ] 变量名与SAP/Table1/结果表一致
│   ├── [ ] 单位标注完整
│   └── [ ] 缩写在图注中解释
├── 导出
│   ├── [ ] SVG 格式已导出（首要）
│   ├── [ ] PNG 300dpi 已导出（预览）
│   ├── [ ] 文件名规范（figureN_类型.png）
│   └── [ ] plt.close(fig) 已调用
└── 期刊合规
    ├── [ ] 尺寸符合目标期刊要求
    ├── [ ] 字号符合目标期刊要求
    └── [ ] 配色符合目标期刊要求
```

---

## 八、与 nature-skills/nature-figure 的对标

本标准在以下维度与 nature-skills/nature-figure 对齐：

| 维度 | nature-figure 规则 | 本标准对应 |
|------|-------------------|----------|
| 强制 rcParams | font.family, font.sans-serif, svg.fonttype | 第一节 |
| 配色系统 | 语义化 PALETTE + DEFAULT_COLOR_ORDER | 第二节 |
| 多面板层级 | 概览→偏差→关系三级递进 | 第三节 |
| 反冗余 | 每面板回答独特问题 | 第3.2节 |
| 导出策略 | SVG 首要，PNG 300dpi 次要 | 第五节 |
| 质量检查 | Reproduction Checklist | 第七节 |
| 面板标签 | 小写粗体字母 a/b/c | 第4.2节 |
| 无边框图例 | legend.frameon = False | 第4.2节 |
| 轴线精简 | 仅左+下轴线 | 第4.2节 |

**差异点**（针对医学统计场景的增强）：
- 增加了期刊配色映射（NEJM/JAMA/Lancet/BMJ/CMJ）
- 增加了 P 值格式化约束（P-R01~R07）
- 增加了变量命名一致性检查
- 增加了医学统计核心图表类型规范（KM/森林图/ROC/校准曲线等）
- 增加了中文字体支持
