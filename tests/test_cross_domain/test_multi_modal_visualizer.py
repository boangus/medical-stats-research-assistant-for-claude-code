"""Unit tests for MultiModalVisualizer.

Tests: create_linked_view four-quadrant, create_summary_dashboard,
single modality, no data exception, save_path.
"""

import os

import matplotlib
import pytest

matplotlib.use('Agg')  # 非交互式后端

from msra_modules.cross_domain import MultiModalVisualizer


class TestMultiModalVisualizer:
    """MultiModalVisualizer unit tests."""

    def test_create_linked_view_four_quadrant(
        self,
        mock_imaging_data,
        mock_imaging_mask,
        mock_expression_data,
        mock_clinical_data,
        mock_realtime_data,
    ):
        """Test 1: create_linked_view — 四象限联动视图"""
        viz = MultiModalVisualizer(figsize=(16, 10), dpi=80)
        fig = viz.create_linked_view(
            imaging_data=mock_imaging_data,
            imaging_mask=mock_imaging_mask,
            expression_data=mock_expression_data,
            clinical_data=mock_clinical_data,
            realtime_data=mock_realtime_data,
        )

        assert fig is not None
        # 应有 4 个子图
        assert len(fig.axes) >= 4
        plt_close(fig)

    def test_create_summary_dashboard(self, mock_radiomics_features, mock_realtime_data):
        """Test 2: create_summary_dashboard — 摘要仪表盘"""
        viz = MultiModalVisualizer(figsize=(12, 4), dpi=80)
        data_sources = {
            "radiomics": mock_radiomics_features,
            "realtime": mock_realtime_data,
        }
        fig = viz.create_summary_dashboard(data_sources)

        assert fig is not None
        # 应有 2 个子图（2 个数据源）
        assert len(fig.axes) >= 2
        plt_close(fig)

    def test_create_linked_view_single_modality(self, mock_expression_data):
        """Test 3: create_linked_view — 单模态（仅表达数据）"""
        viz = MultiModalVisualizer(figsize=(8, 4), dpi=80)
        fig = viz.create_linked_view(
            expression_data=mock_expression_data,
        )

        assert fig is not None
        # 至少 1 个子图
        assert len(fig.axes) >= 1
        plt_close(fig)

    def test_create_linked_view_no_data(self):
        """Test 4: create_linked_view — 无数据时抛出 ValueError"""
        viz = MultiModalVisualizer()
        with pytest.raises(ValueError, match="At least one data source required"):
            viz.create_linked_view()

    def test_create_linked_view_with_save_path(
        self,
        mock_expression_data,
        mock_clinical_data,
        tmp_path,
    ):
        """Test 5: create_linked_view — save_path 保存文件"""
        viz = MultiModalVisualizer(figsize=(8, 6), dpi=80)
        save_path = str(tmp_path / "test_linked_view.png")
        fig = viz.create_linked_view(
            expression_data=mock_expression_data,
            clinical_data=mock_clinical_data,
            save_path=save_path,
        )

        assert fig is not None
        assert os.path.exists(save_path)
        plt_close(fig)

    def test_create_summary_dashboard_with_save_path(
        self,
        mock_radiomics_features,
        tmp_path,
    ):
        """Test 6: create_summary_dashboard — save_path 保存文件"""
        viz = MultiModalVisualizer(figsize=(6, 4), dpi=80)
        save_path = str(tmp_path / "test_dashboard.png")
        fig = viz.create_summary_dashboard(
            {"radiomics": mock_radiomics_features},
            save_path=save_path,
        )

        assert fig is not None
        assert os.path.exists(save_path)
        plt_close(fig)


def plt_close(fig):
    """Close matplotlib figure to free memory."""
    import matplotlib.pyplot as plt
    plt.close(fig)
