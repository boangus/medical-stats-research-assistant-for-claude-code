# MSRA Pipeline Gold Evaluation Set

> 21-tuple gold evaluation set for MSRA pipeline quality measurement.
> Measures data-prep stage detection accuracy against 21 known data quality "pits".

## Origin

The test data `tests/msra_test_data.csv` (600 rows, 24 variables) was designed with
**21 intentional data quality issues** covering all SKILL-defined pitfalls.

This gold set formalizes those 21 issues into structured evaluation tuples that can
be consumed by CI and regression tests.

## Tuple distribution

| ID range | Kind | n | Pipeline stage | Expected result |
|----------|------|---|----------------|----------------|
| 001–004 | `data_value` (值异常) | 4 | Stage 1.5 Gate (项1/2/3) | Data-prep 验证阶段必须标记为 Critical/Warning |
| 005–008 | `logic_conflict` (逻辑矛盾) | 4 | Stage 1.5 Gate (项4/6) | 逻辑一致性检查必须检出 |
| 009–012 | `format_variant` (格式变体) | 4 | Stage 1.5 Gate (项7) | 值规范化模块必须检测并处理 |
| 013–016 | `statistical_concern` (统计隐患) | 4 | Stage 2.5 / 3 Gate | analysis-plan/exec 必须标记为警告 |
| 017–021 | `pipeline_edge` (流程边界) | 5 | 跨阶段 | 触发特定 Checkpoint 或阻断 |

## Threshold contract

- Aggregate: `detection_rate >= 0.90` 至少检出 19/21 个坑
- Per-kind: `detection_rate >= 0.75` 每类至少检出 3/4
- False positive rate: 数据中无该坑时，报告该坑的数量 ≤ 1

## Tuple file naming

`NNN-{kind-slug}-{brief-descriptor}.json` (zero-padded NNN, lowercase-hyphenated).
Filename stem must match the `tuple_id` field inside.

## How to run

```bash
# Run all pipeline gold tests
PYTHONPATH=. python -m scripts.eval_pipeline_gold

# Run specific tuple
PYTHONPATH=. python -m scripts.eval_pipeline_gold --tuple 001
```



