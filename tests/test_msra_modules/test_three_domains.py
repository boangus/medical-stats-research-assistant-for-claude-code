"""
MSRA Modules Tests - 三领域模块测试

运行方式: pytest tests/test_msra_modules/ -v
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestMedicalImagingModule:
    """医学影像模块测试"""

    def test_module_import(self):
        """测试模块导入"""
        from msra_modules.medical_imaging import (
            DICOMLoader, ImagePreprocessor, SegmentationPipeline,
            RadiomicsExtractor, ImagingVisualizer, ImageRegistration
        )
        assert DICOMLoader is not None
        assert ImagePreprocessor is not None
        assert SegmentationPipeline is not None
        assert RadiomicsExtractor is not None
        assert ImagingVisualizer is not None
        assert ImageRegistration is not None

    def test_dicom_loader_initialization(self):
        """测试DICOM加载器初始化"""
        from msra_modules.medical_imaging import DICOMLoader
        loader = DICOMLoader(window_level=40, window_width=400)
        assert loader.window_level == 40
        assert loader.window_width == 400

    def test_preprocessing_normalize(self):
        """测试预处理标准化"""
        from msra_modules.medical_imaging.preprocessing import normalize_intensity
        array = np.array([0, 50, 100, 150, 200, 250], dtype=float)
        normalized = normalize_intensity(array, method="min_max")
        assert normalized.min() == 0
        assert normalized.max() == 1

    def test_radiomics_shape_features(self):
        """测试影像组学形状特征"""
        from msra_modules.medical_imaging import RadiomicsExtractor
        extractor = RadiomicsExtractor()

        # 创建测试掩码 (球形)
        z, y, x = np.ogrid[:20, :20, :20]
        mask = ((z - 10)**2 + (y - 10)**2 + (x - 10)**2 <= 8**2).astype(int)

        features = extractor.extract_shape_features(mask)
        assert "VoxelVolume" in features
        assert features["VoxelVolume"] > 0
        assert "SurfaceArea" in features

    def test_radiomics_firstorder_features(self):
        """测试一阶统计特征"""
        from msra_modules.medical_imaging import RadiomicsExtractor
        extractor = RadiomicsExtractor()

        # 创建测试数据
        np.random.seed(42)
        image = np.random.normal(100, 20, (20, 20, 20))
        mask = np.ones((20, 20, 20), dtype=int)

        features = extractor.extract_firstorder_features(image, mask)
        assert "Mean" in features
        assert "Std" in features
        assert "Skewness" in features
        assert "Kurtosis" in features
        assert 90 < features["Mean"] < 110

    def test_visualizer_creation(self):
        """测试可视化器创建"""
        from msra_modules.medical_imaging import ImagingVisualizer
        viz = ImagingVisualizer(figsize=(10, 8), dpi=150)
        assert viz.figsize == (10, 8)
        assert viz.dpi == 150

    def test_registration_initialization(self):
        """测试配准初始化"""
        from msra_modules.medical_imaging import ImageRegistration
        reg = ImageRegistration(method="rigid")
        assert reg.method == "rigid"


class TestBioinformaticsModule:
    """生物信息学模块测试"""

    def test_module_import(self):
        """测试模块导入"""
        from msra_modules.bioinformatics import (
            ScRNASeqLoader, SingleCellQC, DifferentialExpression,
            CellBenderDenoiser, BioVisualizer, DimensionalityReduction,
            TrajectoryAnalysis
        )
        assert ScRNASeqLoader is not None
        assert SingleCellQC is not None
        assert DifferentialExpression is not None
        assert CellBenderDenoiser is not None
        assert BioVisualizer is not None
        assert DimensionalityReduction is not None
        assert TrajectoryAnalysis is not None

    def test_qc_initialization(self):
        """测试QC初始化"""
        from msra_modules.bioinformatics import SingleCellQC
        qc = SingleCellQC(min_genes=200, max_genes=5000, max_pct_mito=20.0)
        assert qc.min_genes == 200
        assert qc.max_genes == 5000
        assert qc.max_pct_mito == 20.0

    def test_denoiser_initialization(self):
        """测试去噪器初始化"""
        from msra_modules.bioinformatics import CellBenderDenoiser
        denoiser = CellBenderDenoiser(expected_cells=3000, epochs=200)
        assert denoiser.expected_cells == 3000
        assert denoiser.epochs == 200

    def test_visualizer_creation(self):
        """测试可视化器创建"""
        from msra_modules.bioinformatics import BioVisualizer
        viz = BioVisualizer(figsize=(10, 8))
        assert viz.figsize == (10, 8)

    def test_dimensionality_reduction_init(self):
        """测试降维初始化"""
        from msra_modules.bioinformatics import DimensionalityReduction
        dr = DimensionalityReduction(n_pcs=30, n_neighbors=10)
        assert dr.n_pcs == 30
        assert dr.n_neighbors == 10


class TestRealtimeAnalyticsModule:
    """实时分析模块测试"""

    def test_module_import(self):
        """测试模块导入"""
        from msra_modules.realtime_analytics import (
            StreamProcessor, SlidingWindowStats, AnomalyDetector,
            AlertRule, VitalSignsSimulator, AlertSystem,
            RealtimeDashboard, ReportGenerator
        )
        assert StreamProcessor is not None
        assert SlidingWindowStats is not None
        assert AnomalyDetector is not None
        assert AlertRule is not None
        assert VitalSignsSimulator is not None
        assert AlertSystem is not None
        assert RealtimeDashboard is not None
        assert ReportGenerator is not None

    def test_sliding_window_stats(self):
        """测试滑动窗口统计"""
        from msra_modules.realtime_analytics import SlidingWindowStats
        import time

        window = SlidingWindowStats(window_size=10)

        # 添加数据
        for i in range(20):
            window.add(float(i), timestamp=float(i))

        stats = window.get_stats()
        assert stats["count"] <= 20
        assert "mean" in stats
        assert "std" in stats

    def test_anomaly_detector_rules(self):
        """测试异常检测规则"""
        from msra_modules.realtime_analytics import AnomalyDetector, AlertRule, AlertLevel

        detector = AnomalyDetector()

        # 添加规则
        rule = AlertRule(
            name="high_hr",
            metric="heart_rate",
            condition="gt",
            threshold=150,
            level=AlertLevel.CRITICAL
        )
        detector.add_rule(rule)

        # 测试正常值
        alerts = detector.evaluate("heart_rate", 80)
        assert len(alerts) == 0

        # 测试异常值
        alerts = detector.evaluate("heart_rate", 160)
        assert len(alerts) == 1
        assert alerts[0].rule_name == "high_hr"

    def test_default_vital_signs_rules(self):
        """测试默认生命体征规则"""
        from msra_modules.realtime_analytics import AnomalyDetector

        detector = AnomalyDetector()
        detector.add_default_vital_signs_rules()

        rules = detector.get_rules()
        assert len(rules) >= 8  # 至少8个默认规则

        # 测试心动过速
        alerts = detector.evaluate("heart_rate", 160)
        assert len(alerts) > 0

    def test_vital_signs_simulator(self):
        """测试生命体征模拟器"""
        from msra_modules.realtime_analytics import VitalSignsSimulator

        sim = VitalSignsSimulator()
        sample = sim.generate_sample()

        assert 20 < sample.heart_rate < 250
        assert 50 < sample.systolic_bp < 250
        assert 70 < sample.spo2 <= 100
        assert 30 < sample.temperature < 42

    def test_vital_signs_anomaly(self):
        """测试生命体征异常"""
        from msra_modules.realtime_analytics import VitalSignsSimulator

        sim = VitalSignsSimulator()
        sim.trigger_anomaly("tachycardia", duration=60)

        sample = sim.generate_sample()
        assert sample.heart_rate > 150  # 应该是心动过速

    def test_alert_system(self):
        """测试警报系统"""
        from msra_modules.realtime_analytics import AlertSystem, Alert

        system = AlertSystem()

        alert = Alert(
            rule_name="test_rule",
            metric="heart_rate",
            value=160,
            level="critical",
            message="Test alert",
            timestamp=1234567890
        )

        system.send_alert(alert)

        history = system.get_history()
        assert len(history) >= 1

        stats = system.get_statistics()
        assert stats["total_alerts"] >= 1

    def test_stream_processor(self):
        """测试流处理器"""
        from msra_modules.realtime_analytics import StreamProcessor

        processor = StreamProcessor(window_size=60)
        processor.register_metric("heart_rate")

        # 添加数据
        for i in range(10):
            processor.add_data_point("heart_rate", 75 + i)

        stats = processor.get_metric_stats("heart_rate")
        assert stats["count"] == 10
        assert "mean" in stats

    def test_dashboard_creation(self):
        """测试仪表盘创建"""
        from msra_modules.realtime_analytics import RealtimeDashboard

        dashboard = RealtimeDashboard(max_points=100)
        dashboard.add_metric("heart_rate", display_name="心率", unit="bpm")

        dashboard.update("heart_rate", 75.0)

        data = dashboard.get_dashboard_data()
        assert "heart_rate" in data["metrics"]

    def test_report_generator(self):
        """测试报告生成器"""
        from msra_modules.realtime_analytics import ReportGenerator
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)

            filepath = generator.generate_monitoring_report(
                duration="1 hour",
                stats={"heart_rate": {"mean": 75, "std": 5, "min": 60, "max": 100}},
                alerts=[],
                output_format="html"
            )

            assert Path(filepath).exists()


class TestCrossDomainModule:
    """交叉领域模块测试"""

    def test_module_import(self):
        """测试模块导入"""
        from msra_modules.cross_domain import (
            RadiomicsDEGCorrelation, RealtimePredictionModel, MultiModalVisualizer
        )
        assert RadiomicsDEGCorrelation is not None
        assert RealtimePredictionModel is not None
        assert MultiModalVisualizer is not None

    def test_radiomics_deg_correlation(self):
        """测试影像组学-DEG关联"""
        from msra_modules.cross_domain import RadiomicsDEGCorrelation
        import pandas as pd

        correlator = RadiomicsDEGCorrelation(correlation_method="pearson")

        # 创建测试数据
        np.random.seed(42)
        n_samples = 10
        radiomics = pd.DataFrame(
            np.random.randn(n_samples, 3),
            columns=["feat1", "feat2", "feat3"],
            index=[f"sample_{i}" for i in range(n_samples)]
        )
        expression = pd.DataFrame(
            np.random.randn(n_samples, 5),
            columns=["gene1", "gene2", "gene3", "gene4", "gene5"],
            index=[f"sample_{i}" for i in range(n_samples)]
        )

        result = correlator.correlate(radiomics, expression)
        assert "correlations" in result
        assert result["n_total"] == 15  # 3 features × 5 genes

    def test_realtime_prediction_model(self):
        """测试实时预测模型"""
        from msra_modules.cross_domain import RealtimePredictionModel
        import pandas as pd

        model = RealtimePredictionModel(model_type="logistic")

        # 创建训练数据
        np.random.seed(42)
        n_samples = 50
        X = pd.DataFrame(
            np.random.randn(n_samples, 10),
            columns=[f"t_{i}" for i in range(10)]
        )
        y = (X.iloc[:, 0] > 0).astype(int).values

        model.train(X, y)

        # 预测
        result = model.predict(list(X.iloc[0].values))
        assert "prediction" in result
        assert "probability" in result
        assert "risk_level" in result

    def test_multimodal_visualizer(self):
        """测试多模态可视化器"""
        from msra_modules.cross_domain import MultiModalVisualizer

        viz = MultiModalVisualizer(figsize=(12, 8))

        # 创建测试数据
        imaging = np.random.rand(20, 20, 20)
        realtime = {"heart_rate": [70, 72, 75, 73, 71]}

        fig = viz.create_linked_view(
            imaging_data=imaging,
            realtime_data=realtime
        )
        assert fig is not None


class TestCrossModuleIntegration:
    """跨模块集成测试"""

    def test_all_modules_importable(self):
        """测试所有模块可导入"""
        from msra_modules import medical_imaging, bioinformatics, realtime_analytics
        assert medical_imaging is not None
        assert bioinformatics is not None
        assert realtime_analytics is not None

    def test_cross_domain_importable(self):
        """测试交叉领域模块可导入"""
        from msra_modules import cross_domain
        assert cross_domain is not None

    def test_module_versions(self):
        """测试模块版本"""
        from msra_modules.medical_imaging import __version__ as img_ver
        from msra_modules.bioinformatics import __version__ as bio_ver
        from msra_modules.realtime_analytics import __version__ as rt_ver
        from msra_modules.cross_domain import __version__ as cross_ver

        assert img_ver >= "1.0.0"
        assert bio_ver >= "1.0.0"
        assert rt_ver >= "1.0.0"
        assert cross_ver >= "1.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
