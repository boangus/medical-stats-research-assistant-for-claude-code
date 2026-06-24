# Phase 6: 不可变审计日志 🆕

> 借鉴 Data Analysis Copilot (arXiv 2025) 的不可变审计日志机制。
> 临床统计分析必须满足可重复性和合规性要求，审计日志是核心保障。
> **核心原则**：每次分析操作的输入、代码、输出、时间戳必须被记录且不可修改。

---

## 6a. 审计日志结构

```json
{
  "audit_id": "MSRA-2026-0614-001-AUDIT",
  "analysis_id": "MSRA-2026-0614-001",
  "timestamp": "2026-06-14T10:30:45.123Z",
  "stage": "Stage 3: Analysis Exec",
  "phase": "Phase 3: 推断分析",
  "operation": {
    "type": "statistical_analysis",
    "method": "Cox Proportional Hazards",
    "software": "R 4.3.2 / survival 3.5-7"
  },
  "input": {
    "data_hash": "sha256:a1b2c3d4...",
    "sap_version": "v1.2",
    "variables": ["time", "event", "treatment", "age", "sex"]
  },
  "code": {
    "file": "analysis/cox_model.R",
    "hash": "sha256:e5f6g7h8...",
    "lines": "15-42"
  },
  "output": {
    "result_file": "results/cox_results.csv",
    "hash": "sha256:i9j0k1l2...",
    "key_findings": {
      "HR": 0.75,
      "CI_lower": 0.58,
      "CI_upper": 0.97,
      "p_value": 0.028
    }
  },
  "quality_checks": {
    "assumptions": "PH assumption verified (p=0.45)",
    "convergence": "Converged in 4 iterations",
    "warnings": []
  },
  "signature": {
    "agent": "Exec Runner",
    "verifier": "Exec Inference",
    "checksum": "sha256:m3n4o5p6..."
  }
}
```

---

## 6b. 审计日志不可变性保障

| 保障机制 | 实现方式 | 验证方法 |
|---------|---------|---------|
| 写入即锁定 | 日志文件权限设为只读 | 尝试修改 → 权限拒绝 |
| 哈希链 | 每条日志包含前一条日志的哈希 | 链断裂 → 检测到篡改 |
| 时间戳签名 | 使用可信时间源签名 | 时间戳验证 → 确认记录时间 |
| 副本备份 | 日志同步到独立存储 | 主日志损坏 → 从备份恢复 |

---

## 6c. 审计日志记录点

| Phase | 记录内容 | 触发时机 |
|-------|---------|---------|
| Phase 0 | SAP验证+执行前检查结果 | 验证完成时 |
| Phase 1 | 变量构造代码和映射 | 构造完成时 |
| Phase 2 | 描述统计+依从性+安全性结果 | 分析完成时 |
| Phase 3 | 推断分析(含假设检验)结果 | 分析完成时 |
| Phase 4 | 质检结果 | 质检完成时 |
| Phase 5 | 产物清单和哈希 | 产物生成时 |

---

## 6d. 审计日志查询接口

```python
# 查询特定分析的所有审计记录
audit_log.query(analysis_id="MSRA-2026-0614-001")

# 查询特定时间范围的操作
audit_log.query(start_time="2026-06-01", end_time="2026-06-14")

# 验证审计链完整性
audit_log.verify_chain()  # → True/False + 断裂点位置

# 导出合规报告
audit_log.export_compliance_report(format="FDA_21CFR11")
```

---

## 6e. 合规性映射

| 法规要求 | 审计日志字段 | 满足方式 |
|---------|-------------|---------|
| FDA 21 CFR Part 11 | 电子签名、时间戳、不可修改 | signature + timestamp + 哈希链 |
| GCP | 操作可追溯、数据可复现 | input/output hash + code hash |
| ICH E6 | 分析过程记录 | phase + operation + quality_checks |
| GDPR | 数据处理透明 | input variables + purpose |

---

## 6f. 审计日志异常处理

| 异常情况 | 检测方式 | 处理 |
|---------|---------|------|
| 日志写入失败 | 写入操作返回错误 | 暂停分析，提示用户检查存储 |
| 哈希链断裂 | verify_chain() 返回 False | 标记断裂点，记录到安全日志，通知管理员 |
| 时间戳异常 | 时间戳早于前一条记录 | 标记为"时间异常"，需人工审核 |
| 代码哈希不匹配 | 执行代码与记录哈希不同 | 标记为"代码变更"，记录到偏差日志 |

---

## 审计日志铁律

> [IRON RULE] 审计日志记录失败时，分析流程必须暂停。不可在没有审计追踪的情况下继续执行临床统计分析。

**输出**：`{stage_dir}/audit_log.jsonl`（JSON Lines 格式，每行一条记录）
