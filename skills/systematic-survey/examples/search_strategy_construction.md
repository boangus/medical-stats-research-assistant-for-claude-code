# 检索策略构建示例

> 示例: 某药物心血管事件预防效果的 PubMed 检索策略

---

## 研究问题

**PICO**:
- P: 成人心血管高危人群
- I: XXX 药物
- C: 安慰剂
- O: 主要心血管事件 (MACE)

## 检索策略构建过程

### Step 1: 概念分解

| PICO 要素 | 概念 |
|-----------|------|
| P | 心血管疾病 / 冠心病 / 心肌梗死 / 脑卒中 / 高血压 |
| I | XXX 药物 / 药物通用名 / 商品名 |
| C | 安慰剂 / 常规治疗 |
| O | 主要心血管事件 / MACE / 死亡率 |

### Step 2: MeSH 词和自由词

#### Population Block

```
#1 "Cardiovascular Diseases"[MeSH]
#2 "Myocardial Infarction"[MeSH]
#3 "Stroke"[MeSH]
#4 "Hypertension"[MeSH]
#5 cardiovascular[tiab] OR cardiac[tiab] OR heart[tiab]
#6 myocardial infarction[tiab] OR heart attack[tiab]
#7 stroke[tiab] OR cerebrovascular[tiab]
#8 #1 OR #2 OR #3 OR #4 OR #5 OR #6 OR #7
```

#### Intervention Block

```
#9 "XXX"[MeSH] (如有 MeSH 词)
#10 XXX[tiab] OR "商品名"[tiab] OR "药物类别"[tiab]
#11 #9 OR #10
```

### Step 3: 组合

```
#12 #8 AND #11
```

### Step 4: 限制

```
#13 #12 AND (Randomized Controlled Trial[pt] OR Controlled Clinical Trial[pt])
#14 #13 AND English[lang]
```

## 最终检索策略

```
("Cardiovascular Diseases"[MeSH] OR "Myocardial Infarction"[MeSH] OR
 "Stroke"[MeSH] OR "Hypertension"[MeSH] OR
 cardiovascular[tiab] OR cardiac[tiab] OR heart[tiab] OR
 myocardial infarction[tiab] OR stroke[tiab]) AND
(XXX[tiab] OR "商品名"[tiab]) AND
(Randomized Controlled Trial[pt] OR Controlled Clinical Trial[pt])
```

## 检索结果

| 数据库 | 结果数 | 检索日期 |
|--------|--------|---------|
| PubMed | 156 | 2026-06-22 |
| Embase | 203 | 2026-06-22 |
| Cochrane | 45 | 2026-06-22 |
| **总去重后** | **267** | - |

## 检索策略验证

- ✅ 已由第二位人员审核
- ✅ 已测试敏感性（包含所有已知符合文献）
- ✅ 已记录各数据库检索语法差异
