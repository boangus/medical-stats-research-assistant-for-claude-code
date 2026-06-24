#!/usr/bin/env python3
"""
分析语言选择一致性测试

测试分析语言选择在整个流程中的一致性。
"""

import os

# 添加项目根目录到Python路径
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.passport.passport import PassportError, PassportManager


class TestLanguageConsistency:
    """分析语言一致性测试类"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.passport_path = os.path.join(self.temp_dir, "passport.json")

    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_language_selection_flow(self):
        """测试语言选择流程"""
        # 1. 创建Passport管理器
        pm = PassportManager(self.passport_path)

        # 2. 验证初始状态：未选择语言
        selected, message = pm.verify_analysis_language_selected()
        assert not selected
        assert "未选择" in message

        # 3. 获取语言选择（应该返回None）
        language = pm.get_analysis_language()
        assert language is None

        # 4. 选择R语言
        artifact_id = pm.set_analysis_language("R", confirmed_by="test_user")
        assert artifact_id == "analysis_language"

        # 5. 验证选择状态
        selected, message = pm.verify_analysis_language_selected()
        assert selected
        assert "R" in message

        # 6. 获取语言选择
        language = pm.get_analysis_language()
        assert language == "R"

        # 7. 验证记录数据完整性
        artifact = pm.get_artifact("analysis_language")
        assert artifact is not None
        assert artifact['status'] == 'completed'
        assert artifact['type'] == 'language_selection'

        language_data = artifact['language_data']
        assert language_data['language'] == 'R'
        assert language_data['language_name'] == 'R'
        assert language_data['confirmed_by'] == 'test_user'
        assert language_data['confirmation_type'] == 'mandatory_selection'

    def test_language_selection_python(self):
        """测试选择Python语言"""
        pm = PassportManager(self.passport_path)

        # 选择Python语言
        pm.set_analysis_language("Python", confirmed_by="test_user")

        # 验证选择状态
        selected, message = pm.verify_analysis_language_selected()
        assert selected
        assert "Python" in message

        # 获取语言选择
        language = pm.get_analysis_language()
        assert language == "Python"

    def test_language_selection_invalid(self):
        """测试无效的语言选择"""
        pm = PassportManager(self.passport_path)

        # 尝试设置无效的语言
        with pytest.raises(PassportError) as exc_info:
            pm.set_analysis_language("Java")
        assert "无效的分析语言" in str(exc_info.value)

    def test_language_selection_idempotent(self):
        """测试语言选择的幂等性"""
        pm = PassportManager(self.passport_path)

        # 第一次选择
        pm.set_analysis_language("R", confirmed_by="user1")
        artifact1 = pm.get_artifact("analysis_language")

        # 第二次选择（应该更新而不是创建新记录）
        pm.set_analysis_language("Python", confirmed_by="user2")
        artifact2 = pm.get_artifact("analysis_language")

        # 应该是同一条记录
        assert artifact1['id'] == artifact2['id']
        # 但语言应该更新
        assert artifact2['language_data']['language'] == 'Python'
        assert artifact2['language_data']['confirmed_by'] == 'user2'

    def test_language_consistency_across_stages(self):
        """测试跨阶段的语言一致性"""
        pm = PassportManager(self.passport_path)

        # 选择R语言
        pm.set_analysis_language("R", confirmed_by="test_user")

        # 模拟多个阶段读取语言选择
        for stage in ["stage_1", "stage_2", "stage_3", "stage_4"]:
            language = pm.get_analysis_language()
            assert language == "R", f"Stage {stage} 语言选择不一致"

    def test_language_selection_required_for_analysis(self):
        """测试分析执行前必须选择语言"""
        pm = PassportManager(self.passport_path)

        # 验证未选择语言时的状态
        selected, _ = pm.verify_analysis_language_selected()
        assert not selected

        # 选择语言后
        pm.set_analysis_language("R", confirmed_by="test_user")
        selected, _ = pm.verify_analysis_language_selected()
        assert selected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
