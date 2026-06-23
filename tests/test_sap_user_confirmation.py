#!/usr/bin/env python3
"""
SAP 用户确认流程测试

测试统计分析计划生成后的强制用户确认功能。
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.passport.passport import PassportManager, PassportError
from shared.sap.validate_sap import SAPValidator


class TestSAPUserConfirmation:
    """SAP 用户确认测试类"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.passport_path = os.path.join(self.temp_dir, "passport.json")
        self.sap_path = os.path.join(self.temp_dir, "test_sap.md")

        # 创建测试SAP文件
        self._create_test_sap()

    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_sap(self):
        """创建测试SAP文件"""
        sap_content = """---
study_id: "TEST001"
version: "1.0"
created_date: "2026-06-22"
status: "approved"
study_type: "RCT"
---

# 统计分析计划 (Statistical Analysis Plan)

## 1. 研究概述

### 1.1 研究设计和目的
- 研究类型: RCT
- 研究目的: 评估药物A对HbA1c的影响

## 2. 分析人群

### 2.1 意向性治疗人群 (ITT)
- 定义: 所有随机化患者

## 3. 终点定义

### 3.1 主要终点
- 名称: HbA1c变化
- 定义: 基线到24周的HbA1c变化

## 4. 统计方法

### 4.1 主要分析
- 方法: ANCOVA
- 调整变量: baseline_hba1c, age

## 5. 多重比较控制
- 主要终点单独检验

## 7. 变量构造定义

| 变量名 | 类型 | 构造公式 | 切点/分类 | 依据 | 缺失处理 |
|--------|------|---------|----------|------|---------|
| age | 连续 | 入组日期 - 出生日期（年） | - | 标准人口学 | 删除 |
| hba1c_change | 连续 | 24周HbA1c - 基线HbA1c | - | 主要终点 | 多重插补 |

## 8. 分析规范表

| 分析ID | 分析名称 | 人群 | 方法 | 主要变量 | 调整变量 | 缺失处理 | 假设检验 |
|--------|---------|------|------|---------|---------|---------|---------|
| A1 | 主要终点分析 | ITT | ANCOVA | hba1c_change | baseline_hba1c, age | 多重插补 | F-test |
"""

        with open(self.sap_path, 'w', encoding='utf-8') as f:
            f.write(sap_content)

    def test_sap_user_confirmation_flow(self):
        """测试SAP用户确认流程"""
        # 1. 创建Passport管理器
        pm = PassportManager(self.passport_path)

        # 2. 添加SAP产物
        pm.add_artifact({
            "id": "sap",
            "stage": "stage_2",
            "name": "统计分析计划",
            "type": "document",
            "format": "markdown",
            "status": "completed",
            "path": self.sap_path
        })

        # 3. 验证初始状态：用户未确认SAP
        confirmed, message = pm.verify_sap_user_confirmed()
        assert not confirmed
        assert "不存在" in message

        # 4. 检查前置条件：stage_2.5需要sap_user_confirmed
        ok, missing = pm.verify_prerequisites("stage_2.5")
        assert not ok
        assert "sap_user_confirmed" in missing

        # 5. 用户确认SAP
        confirmation_id = pm.confirm_sap_by_user()
        assert confirmation_id == "sap_user_confirmed"

        # 6. 验证确认状态
        confirmed, message = pm.verify_sap_user_confirmed()
        assert confirmed
        assert "已获用户确认" in message

        # 7. 再次检查前置条件：现在应该通过
        ok, missing = pm.verify_prerequisites("stage_2.5")
        assert ok
        assert len(missing) == 0

    def test_sap_user_confirmation_required_for_stage_2_5(self):
        """测试Stage 2.5必须要求用户确认SAP"""
        pm = PassportManager(self.passport_path)

        # 添加SAP产物
        pm.add_artifact({
            "id": "sap",
            "stage": "stage_2",
            "name": "统计分析计划",
            "type": "document",
            "format": "markdown",
            "status": "completed",
            "path": self.sap_path
        })

        # 尝试进入Stage 2.5（应该失败）
        ok, missing = pm.verify_prerequisites("stage_2.5")
        assert not ok
        assert "sap_user_confirmed" in missing

        # 用户确认SAP
        pm.confirm_sap_by_user()

        # 再次尝试进入Stage 2.5（应该成功）
        ok, missing = pm.verify_prerequisites("stage_2.5")
        assert ok

    def test_sap_validation_with_user_confirmation(self):
        """测试SAP验证包含用户确认状态"""
        # 1. 创建Passport并添加SAP产物
        pm = PassportManager(self.passport_path)
        pm.add_artifact({
            "id": "sap",
            "stage": "stage_2",
            "name": "统计分析计划",
            "type": "document",
            "format": "markdown",
            "status": "completed",
            "path": self.sap_path
        })

        # 2. 创建SAP验证器
        validator = SAPValidator()

        # 3. 验证SAP内容
        validation_result = validator.validate_sap(self.sap_path)
        assert validation_result['valid']

        # 4. 验证用户确认状态（未确认）
        confirmation_result = validator.validate_user_confirmation(self.passport_path)
        assert not confirmation_result['confirmed']
        assert confirmation_result['severity'] == 'P0'

        # 5. 用户确认SAP
        pm.confirm_sap_by_user()

        # 6. 再次验证用户确认状态（已确认）
        confirmation_result = validator.validate_user_confirmation(self.passport_path)
        assert confirmation_result['confirmed']
        assert confirmation_result['severity'] == 'INFO'

        # 7. 生成包含用户确认状态的报告
        report = validator.generate_validation_report(validation_result, confirmation_result)
        assert "SAP 用户确认状态" in report
        assert "已确认" in report

    def test_sap_user_confirmation_data_integrity(self):
        """测试SAP用户确认数据的完整性"""
        pm = PassportManager(self.passport_path)

        # 用户确认SAP
        pm.confirm_sap_by_user(confirmed_by="test_user")

        # 获取确认记录
        confirmation = pm.get_artifact("sap_user_confirmed")
        assert confirmation is not None
        assert confirmation['status'] == 'completed'
        assert confirmation['type'] == 'confirmation'

        # 验证确认数据
        confirmation_data = confirmation['confirmation_data']
        assert confirmation_data['sap_id'] == 'sap'
        assert confirmation_data['confirmed_by'] == 'test_user'
        assert confirmation_data['confirmation_type'] == 'mandatory_review'
        assert 'confirmed_at' in confirmation_data

    def test_sap_user_confirmation_idempotent(self):
        """测试SAP用户确认的幂等性"""
        pm = PassportManager(self.passport_path)

        # 第一次确认
        pm.confirm_sap_by_user(confirmed_by="user1")
        confirmation1 = pm.get_artifact("sap_user_confirmed")

        # 第二次确认（应该更新而不是创建新记录）
        pm.confirm_sap_by_user(confirmed_by="user2")
        confirmation2 = pm.get_artifact("sap_user_confirmed")

        # 应该是同一条记录
        assert confirmation1['id'] == confirmation2['id']
        # 但确认人应该更新
        assert confirmation2['confirmation_data']['confirmed_by'] == 'user2'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
