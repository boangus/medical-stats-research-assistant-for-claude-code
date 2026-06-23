# Search Strategy Template

> 系统综述检索策略模板

---

## 检索概述

| 项目 | 内容 |
|------|------|
| 检索日期 | [YYYY-MM-DD] |
| 检索人员 | [姓名] |
| 审核人员 | [姓名] |
| 数据库 | [列表] |
| 总检索结果 | [数量] |

---

## 检索策略

### PubMed 检索策略

```
#1 "Population Term 1"[MeSH] OR "Population Term 2"[tiab] OR ...
    (Population Block)

#2 "Intervention Term 1"[MeSH] OR "Intervention Term 2"[tiab] OR ...
    (Intervention/Exposure Block)

#3 "Outcome Term 1"[MeSH] OR "Outcome Term 2"[tiab] OR ...
    (Outcome Block) [可选]

#4 #1 AND #2
#5 #3 [如使用结局块]
#6 #4 AND #5

Filters: [语言/时间/研究类型限制]
```

**结果数**: [N]

### Embase 检索策略

```
#1 'population term'/exp OR 'population term':ti,ab,kw
   (Population Block)

#2 'intervention term'/exp OR 'intervention term':ti,ab,kw
   (Intervention/Exposure Block)

#3 #1 AND #2

Limits: [限制条件]
```

**结果数**: [N]

### Cochrane Library 检索策略

```
#1 MeSH descriptor: [Population] explode all trees
#2 "population term":ti,ab,kw
#3 #1 OR #2
...
```

**结果数**: [N]

---

## 检索词详表

### Population 检索词

| 类型 | 检索词 | 数据库 |
|------|--------|--------|
| MeSH | [术语] | PubMed |
| Emtree | [术语] | Embase |
| 自由词 | [术语] | 全部 |
| 同义词 | [术语] | 全部 |

### Intervention/Exposure 检索词

| 类型 | 检索词 | 数据库 |
|------|--------|--------|
| MeSH | [术语] | PubMed |
| Emtree | [术语] | Embase |
| 自由词 | [术语] | 全部 |

---

## 检索验证

- [ ] 检索策略已覆盖所有 PICO 要素
- [ ] 检索策略已由第二位人员审核
- [ ] 已测试检索策略的敏感性和特异性
- [ ] 已记录各数据库的去重结果
