# TCM 辨证论治变量编码规范

> 中医临床研究中的变量标准化编码方案
> 更新日期: 2026-06-24

---

## 1. 八纲辨证编码

### 1.1 阴阳总纲

| 编码 | 证型 | 定义 |
|------|------|------|
| YIN | 阴证 | 里、虚、寒证的总称 |
| YANG | 阳证 | 表、实、热证的总称 |

### 1.2 表里辨证

| 编码 | 证型 | 定义 | 典型症状 |
|------|------|------|---------|
| BIAO | 表证 | 外邪侵袭肌表 | 恶寒发热、脉浮、苔薄 |
| LI | 里证 | 病在脏腑气血 | 但热不寒/但寒不热、脉沉 |
| BAN_BIAO_BAN_LI | 半表半里证 | 邪在少阳 | 寒热往来、胸胁苦满 |

### 1.3 寒热辨证

| 编码 | 证型 | 定义 | 典型症状 |
|------|------|------|---------|
| HAN | 寒证 | 阳气不足/阴寒内盛 | 畏寒喜暖、口淡不渴、舌淡苔白 |
| RE | 热证 | 阳热亢盛/阴虚内热 | 发热口渴、便秘尿黄、舌红苔黄 |
| HAN_RE_CUO_ZA | 寒热错杂证 | 寒热并存 | 上热下寒、表寒里热 |

### 1.4 虚实辨证

| 编码 | 证型 | 定义 | 典型症状 |
|------|------|------|---------|
| XU | 虚证 | 正气不足 | 气短乏力、面色淡白、脉虚无力 |
| SHI | 实证 | 邪气亢盛 | 腹胀拒按、便秘、脉实有力 |
| XU_SHI_JIA_ZA | 虚实夹杂证 | 虚实并存 | 本虚标实 |

## 2. 脏腑辨证编码

### 2.1 五脏证型

| 脏腑 | 编码 | 常见证型 | 编码 |
|------|------|---------|------|
| 心 | HEART | 心气虚 | HEART_QI_XU |
| | | 心血虚 | HEART_BLOOD_XU |
| | | 心阴虚 | HEART_YIN_XU |
| | | 心阳虚 | HEART_YANG_XU |
| | | 心血瘀阻 | HEART_BLOOD_STASIS |
| 肝 | LIVER | 肝气郁结 | LIVER_QI_STAGNATION |
| | | 肝火上炎 | LIVER_FIRE |
| | | 肝血虚 | LIVER_BLOOD_XU |
| | | 肝阴虚 | LIVER_YIN_XU |
| | | 肝阳上亢 | LIVER_YANG_RISING |
| 脾 | SPLEEN | 脾气虚 | SPLEEN_QI_XU |
| | | 脾阳虚 | SPLEEN_YANG_XU |
| | | 脾虚湿困 | SPLEEN_DAMPNESS |
| | | 脾不统血 | SPLEEN_BLOOD_CONTROL |
| 肺 | LUNG | 肺气虚 | LUNG_QI_XU |
| | | 肺阴虚 | LUNG_YIN_XU |
| | | 风寒束肺 | LUNG_WIND_COLD |
| | | 痰湿阻肺 | LUNG_PHLEGM_DAMPNESS |
| 肾 | KIDNEY | 肾气虚 | KIDNEY_QI_XU |
| | | 肾阳虚 | KIDNEY_YANG_XU |
| | | 肾阴虚 | KIDNEY_YIN_XU |
| | | 肾精不足 | KIDNEY_ESSENCE_DEFICIENCY |

### 2.2 六腑证型

| 腑 | 编码 | 常见证型 | 编码 |
|------|------|---------|------|
| 胆 | GALLBLADDER | 胆郁痰扰 | GB_PHLEGM_DISTURB |
| 胃 | STOMACH | 胃气虚 | STOMACH_QI_XU |
| | | 胃阴虚 | STOMACH_YIN_XU |
| | | 胃热炽盛 | STOMACH_HEAT |
| 小肠 | SMALL_INTESTINE | 小肠实热 | SI_HEAT |
| 大肠 | LARGE_INTESTINE | 大肠湿热 | LI_DAMP_HEAT |
| 膀胱 | BLADDER | 膀胱湿热 | BLADDER_DAMP_HEAT |

## 3. 证候量化评分

### 3.1 主症量化标准（4级）

| 分值 | 程度 | 描述 |
|------|------|------|
| 0 | 无 | 无该症状 |
| 2 | 轻 | 偶有发作，程度轻，不影响日常 |
| 4 | 中 | 时有发作，程度中等，部分影响日常 |
| 6 | 重 | 频繁发作，程度重，明显影响日常 |

### 3.2 次症量化标准（4级）

| 分值 | 程度 | 描述 |
|------|------|------|
| 0 | 无 | 无该症状 |
| 1 | 轻 | 偶有发作 |
| 2 | 中 | 时有发作 |
| 3 | 重 | 频繁发作 |

### 3.3 证候疗效判定

| 疗效等级 | 判定标准 |
|---------|---------|
| 痊愈 | 证候积分减少 ≥ 95% |
| 显效 | 证候积分减少 70%-94% |
| 有效 | 证候积分减少 30%-69% |
| 无效 | 证候积分减少 < 30% |

**计算公式**: 疗效指数 = (治疗前积分 - 治疗后积分) / 治疗前积分 × 100%

## 4. 中药编码

### 4.1 方剂组成编码格式

```json
{
  "formula_name": "六味地黄丸",
  "formula_code": "LWDHW",
  "source": "《小儿药证直诀》",
  "composition": {
    "sovereign": [
      {"herb": "熟地黄", "latin": "Rehmanniae Radix Praeparata", "dose_g": 24, "code": "SDH"}
    ],
    "minister": [
      {"herb": "山茱萸", "latin": "Corni Fructus", "dose_g": 12, "code": "SZY"},
      {"herb": "山药", "latin": "Dioscoreae Rhizoma", "dose_g": 12, "code": "SY"}
    ],
    "assistant": [
      {"herb": "泽泻", "latin": "Alismatis Rhizoma", "dose_g": 9, "code": "ZX"},
      {"herb": "茯苓", "latin": "Poria", "dose_g": 9, "code": "FL"}
    ],
    "envoy": [
      {"herb": "牡丹皮", "latin": "Moutan Cortex", "dose_g": 9, "code": "MDP"}
    ]
  }
}
```

### 4.2 常用方剂编码

| 方剂名 | 编码 | 来源 | 功效 |
|--------|------|------|------|
| 四君子汤 | SJZT | 《太平惠民和剂局方》 | 益气健脾 |
| 四物汤 | SWT | 《太平惠民和剂局方》 | 补血调血 |
| 六味地黄丸 | LWDHW | 《小儿药证直诀》 | 滋补肾阴 |
| 逍遥散 | XYS | 《太平惠民和剂局方》 | 疏肝解郁 |
| 桂枝汤 | GZT | 《伤寒论》 | 解肌发表 |
| 麻黄汤 | MHT | 《伤寒论》 | 发汗解表 |

## 5. 经穴编码 (WHO Standard)

### 5.1 十四经穴编码格式

```
编码规则: 经络缩写 + 序号
示例: LU1 (中府), LI4 (合谷), ST36 (足三里)
```

### 5.2 常用穴位编码

| 经络 | 编码前缀 | 穴位示例 |
|------|---------|---------|
| 手太阴肺经 | LU | LU1(中府), LU7(列缺), LU9(太渊) |
| 手阳明大肠经 | LI | LI4(合谷), LI11(曲池), LI20(迎香) |
| 足阳明胃经 | ST | ST36(足三里), ST25(天枢), ST44(内庭) |
| 足太阴脾经 | SP | SP6(三阴交), SP9(阴陵泉), SP10(血海) |
| 手少阴心经 | HT | HT7(神门), HT5(通里) |
| 手太阳小肠经 | SI | SI3(后溪), SI6(养老) |
| 足太阳膀胱经 | BL | BL23(肾俞), BL40(委中), BL60(昆仑) |
| 足少阴肾经 | KI | KI3(太溪), KI7(复溜) |
| 手厥阴心包经 | PC | PC6(内关), PC8(劳宫) |
| 手少阳三焦经 | SJ | SJ5(外关), SJ21(耳门) |
| 足少阳胆经 | GB | GB20(风池), GB34(阳陵泉), GB39(悬钟) |
| 足厥阴肝经 | LR | LR3(太冲), LR13(章门) |
| 督脉 | GV | GV20(百会), GV26(水沟) |
| 任脉 | CV | CV4(关元), CV6(气海), CV17(膻中) |

### 5.3 耳穴编码

| 区域 | 编码 | 穴位 |
|------|------|------|
| 耳垂 | LO | 扁桃体(LO1-LO4), 目1(LO5), 目2(LO6) |
| 对耳屏 | AT | 枕(AT1), 额(AT2), 颞(AT3), 皮质下(AT4) |
| 耳屏 | TG | 外耳(TG1), 屏尖(TG2), 肾上腺(TG2P) |
| 三角窝 | TF | 神门(TF4), 盆腔(TF5), 内生殖器(TF2) |
| 耳甲 | CO/HX | 心(CO15), 肺(CO14), 肝(CO12), 脾(CO13), 肾(CO10) |

## 6. Python 辅助函数

```python
# TCM 变量编码辅助工具
TCM_ENCODING = {
    "BIAO": {"cn": "表证", "en": "Exterior Syndrome"},
    "LI": {"cn": "里证", "en": "Interior Syndrome"},
    "HAN": {"cn": "寒证", "en": "Cold Syndrome"},
    "RE": {"cn": "热证", "en": "Heat Syndrome"},
    "XU": {"cn": "虚证", "en": "Deficiency Syndrome"},
    "SHI": {"cn": "实证", "en": "Excess Syndrome"},
}

def encode_syndrome(syndrome_type, organ=None, pattern=None):
    """
    生成标准化证候编码
    
    Parameters
    ----------
    syndrome_type : str
        八纲辨证类型 (BIAO/LI/HAN/RE/XU/SHI)
    organ : str, optional
        脏腑 (HEART/LIVER/SPLEEN/LUNG/KIDNEY)
    pattern : str, optional
        证型 (QI_XU/BLOOD_XU/YIN_XU/YANG_XU/...)
    
    Returns
    -------
    str : 标准编码
    """
    if organ and pattern:
        return f"{organ}_{pattern}"
    return syndrome_type

def calculate_syndrome_score(symptoms: dict) -> dict:
    """
    计算证候总分
    
    Parameters
    ----------
    symptoms : dict
        {症状名: 分值} 字典
    
    Returns
    -------
    dict : 总分、主症分、次症分
    """
    total = sum(symptoms.values())
    return {
        "total_score": total,
        "symptom_count": len(symptoms),
        "mean_score": total / len(symptoms) if symptoms else 0
    }

def syndrome_efficacy(pre_score, post_score):
    """
    证候疗效判定
    
    Returns
    -------
    str : 疗效等级
    """
    if pre_score == 0:
        return "无法判定（治疗前积分为0）"
    
    reduction = (pre_score - post_score) / pre_score * 100
    
    if reduction >= 95:
        return "痊愈"
    elif reduction >= 70:
        return "显效"
    elif reduction >= 30:
        return "有效"
    else:
        return "无效"
```

## 参考文献

1. 国家药品监督管理局. 中药新药临床研究指导原则. 2002.
2. WHO Standard Acupuncture Point Locations in the Western Pacific Region. 2008.
3. 中国中医药学名词审定委员会. 中医药学名词. 科学出版社. 2005.
4. 孙广仁. 中医基础理论. 中国中医药出版社. 2007.
5. 国家中医药管理局. 中医病证诊断疗效标准. 1994.
