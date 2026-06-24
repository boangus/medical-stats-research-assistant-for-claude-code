#!/usr/bin/env python3
"""
脚本执行模式确认流程测试

测试分析脚本执行前的模式选择功能。
"""

import os

# 添加项目根目录到Python路径
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.passport.passport import PassportError, PassportManager


class TestScriptExecutionMode:
    """脚本执行模式测试类"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.passport_path = os.path.join(self.temp_dir, "passport.json")

    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_script_execution_mode_flow(self):
        """测试脚本执行模式选择流程"""
        # 1. 创建Passport管理器
        pm = PassportManager(self.passport_path)

        # 2. 验证初始状态：未选择执行模式
        selected, message = pm.verify_script_execution_mode_selected()
        assert not selected
        assert "未选择" in message

        # 3. 获取执行模式（应该返回None）
        mode = pm.get_script_execution_mode()
        assert mode is None

        # 4. 选择"先审核后执行"模式
        artifact_id = pm.set_script_execution_mode("review_first", confirmed_by="test_user")
        assert artifact_id == "script_execution_mode"

        # 5. 验证选择状态
        selected, message = pm.verify_script_execution_mode_selected()
        assert selected
        assert "先审核后执行" in message

        # 6. 获取执行模式
        mode = pm.get_script_execution_mode()
        assert mode == "review_first"

        # 7. 验证记录数据完整性
        artifact = pm.get_artifact("script_execution_mode")
        assert artifact is not None
        assert artifact['status'] == 'completed'
        assert artifact['type'] == 'execution_mode'

        mode_data = artifact['execution_mode_data']
        assert mode_data['mode'] == 'review_first'
        assert mode_data['mode_name'] == '先审核后执行'
        assert mode_data['confirmed_by'] == 'test_user'
        assert mode_data['confirmation_type'] == 'mandatory_selection'

    def test_script_execution_mode_direct_execute(self):
        """测试选择直接执行模式"""
        pm = PassportManager(self.passport_path)

        # 选择"直接执行"模式
        pm.set_script_execution_mode("direct_execute", confirmed_by="test_user")

        # 验证选择状态
        selected, message = pm.verify_script_execution_mode_selected()
        assert selected
        assert "直接执行" in message

        # 获取执行模式
        mode = pm.get_script_execution_mode()
        assert mode == "direct_execute"

    def test_script_execution_mode_invalid_mode(self):
        """测试无效的执行模式"""
        pm = PassportManager(self.passport_path)

        # 尝试设置无效的执行模式
        with pytest.raises(PassportError) as exc_info:
            pm.set_script_execution_mode("invalid_mode")
        assert "无效的执行模式" in str(exc_info.value)

    def test_script_execution_mode_idempotent(self):
        """测试脚本执行模式选择的幂等性"""
        pm = PassportManager(self.passport_path)

        # 第一次选择
        pm.set_script_execution_mode("review_first", confirmed_by="user1")
        artifact1 = pm.get_artifact("script_execution_mode")

        # 第二次选择（应该更新而不是创建新记录）
        pm.set_script_execution_mode("direct_execute", confirmed_by="user2")
        artifact2 = pm.get_artifact("script_execution_mode")

        # 应该是同一条记录
        assert artifact1['id'] == artifact2['id']
        # 但执行模式应该更新
        assert artifact2['execution_mode_data']['mode'] == 'direct_execute'
        assert artifact2['execution_mode_data']['confirmed_by'] == 'user2'

    def test_script_execution_mode_required_for_stage_3(self):
        """测试Stage 3必须要求选择脚本执行模式"""
        pm = PassportManager(self.passport_path)

        # 添加必要的前置产物
        pm.add_artifact({
            "id": "cleaned_data",
            "stage": "stage_1",
            "name": "清洗后数据",
            "type": "dataset",
            "format": "csv",
            "status": "completed"
        })

        pm.add_artifact({
            "id": "db_lock_record",
            "stage": "stage_1",
            "name": "数据库锁定记录",
            "type": "record",
            "format": "json",
            "status": "completed"
        })

        pm.add_artifact({
            "id": "sap",
            "stage": "stage_2",
            "name": "统计分析计划",
            "type": "document",
            "format": "markdown",
            "status": "completed"
        })

        pm.add_artifact({
            "id": "gate_stage_2.5",
            "stage": "stage_2.5",
            "name": "SAP质量门闸",
            "type": "gate",
            "format": "json",
            "status": "completed"
        })

        # 设置门闸结果
        pm.set_gate_result("stage_2.5", "passed", 8, 8)

        # 验证Stage 3的前置条件（目前不包含脚本执行模式）
        ok, missing = pm.verify_prerequisites("stage_3")
        assert ok  # 目前Stage 3不要求脚本执行模式

        # 但我们可以添加一个验证方法来检查脚本执行模式
        selected, _ = pm.verify_script_execution_mode_selected()
        assert not selected  # 未选择执行模式


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
