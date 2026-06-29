# 数值格式变体正则模式清单

## 一、检测下限 (Lower Limit of Detection)

### 符号标记
| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 小于号 | `^<\s*(\d+\.?\d*)` | `<1.5` | threshold=1.5, direction=lower |
| 小于等于 | `^≤\s*(\d+\.?\d*)` | `≤0.05` | threshold=0.05, direction=lower |
| 小于(非) | `^<\s*(\d+\.?\d*)\s*$` | `< 0.001` | threshold=0.001, direction=lower |

### 中文标记
| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 小于 | `^小[于於]\s*(\d+\.?\d*)` | `小于1.5` | threshold=1.5, direction=lower |
| 不超过 | `^不[超[过]?]\s*(\d+\.?\d*)` | `不超过0.5` | threshold=0.5, direction=lower |
| 不高于/不大于 | `^不[高[于]?\|[大[于]?]]\s*(\d+\.?\d*)` | `不高于10` | threshold=10, direction=lower |
| 低于 | `^低[于於]?\s*(\d+\.?\d*)` | `低于0.1` | threshold=0.1, direction=lower |
| 不足 | `^不足\s*(\d+\.?\d*)` | `不足5` | threshold=5, direction=lower |
| 未达 | `^未达\s*(\d+\.?\d*)` | `未达3` | threshold=3, direction=lower |

## 二、检测上限 (Upper Limit of Detection)

### 符号标记
| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 大于号 | `^>\s*(\d+\.?\d*)` | `>200` | threshold=200, direction=upper |
| 大于等于 | `^≥\s*(\d+\.?\d*)` | `≥1000` | threshold=1000, direction=upper |

### 中文标记
| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 大于 | `^大[于於]\s*(\d+\.?\d*)` | `大于200` | threshold=200, direction=upper |
| 超过 | `^超[过]?\s*(\d+\.?\d*)` | `超过1000` | threshold=1000, direction=upper |
| 不低于/不小于 | `^不[低[于]?\|小[于]?]\s*(\d+\.?\d*)` | `不低于50` | threshold=50, direction=upper |
| 至少 | `^至[少]\s*(\d+\.?\d*)` | `至少100` | threshold=100, direction=upper |
| 高于 | `^高[于於]?\s*(\d+\.?\d*)` | `高于100` | threshold=100, direction=upper |

## 三、逗号分隔多值

| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 逗号分隔 | `^(\d+\.?\d*)\s*[,，]\s*(\d+\.?\d*)\s*([,，]\s*\d+\.?\d*)*$` | `1,2,3` | values=[1.0, 2.0, 3.0] |
| 中英文逗号 | 同上(逗号含全角) | `3.5，4.2` | values=[3.5, 4.2] |
| 空格分隔 | `^(\d+\.?\d*)\s+(\d+\.?\d*)$` | `1.5 2.3` | values=[1.5, 2.3] |
| 分号分隔 | `^(\d+\.?\d*)\s*[;；]\s*(\d+\.?\d*)$` | `5;6;7` | values=[5, 6, 7] |

## 四、范围表示

| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 短横范围 | `^(\d+\.?\d*)\s*[-~]\s*(\d+\.?\d*)$` | `5-10` | type=range, lo=5, hi=10 |
| 波浪范围 | `^(\d+\.?\d*)\s*[~～]\s*(\d+\.?\d*)$` | `3.5～7.2` | type=range, lo=3.5, hi=7.2 |
| 至 | `^(\d+\.?\d*)\s*[至到]\s*(\d+\.?\d*)$` | `5至10` | type=range, lo=5, hi=10 |

## 五、中文数字

| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 中文数字 | `^[零一二三四五六七八九十百千万亿点]+\s*$` | `五` | type=chinese_num, detected |

> **注意**: 中文数字（如"五"）需要用户确认是否转换为数字"5"。
> 中医临床数据中有些是以中文数字表示等级或评分，不应自动转换。

## 六、特殊标记

| 模式 | 正则 | 示例 | 匹配结果 |
|------|------|------|---------|
| 缺失标记 | `^(NA|N/A|na|n/a|空|未查|未做|待查)$` | `未查` | type=missing_code |
| 文本描述 | `^(无|正常|阴性|-)$` | `正常` | type=text_descriptive |

> 特殊标记不在值规范化的处理范围内——它们由Phase 2（缺失值处理）负责。
> 这里仅作为检测过滤依据，避免与缺失值处理冲突。

## 使用方式

```python
from numeric_normalizer import NumericVariantDetector

detector = NumericVariantDetector()
results = detector.detect_variants(df, column="PSA")
detector.show_summary(results)
```

## 扩展说明

如需新增正则模式，在 `PATTERNS` 字典中添加即可，无需修改检测逻辑：

```python
PATTERNS["new_type"] = [
    {"name": "模式描述", "regex": r"^新正则$", "parser": my_parser_func}
]
```

每个模式条目的 `parser` 函数接收 (match对象) 并返回结构化的解析结果。



