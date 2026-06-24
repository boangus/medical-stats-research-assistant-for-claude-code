"""Unit tests for RealtimePredictionModel.

Tests: train() + predict(), feature extraction, risk level,
evaluate(), model type switching.
"""

import numpy as np
import pandas as pd
import pytest

from msra_modules.cross_domain import RealtimePredictionModel


class TestRealtimePredictionModel:
    """RealtimePredictionModel unit tests."""

    def test_train_and_predict(self, mock_historical_data, mock_labels):
        """Test 1: train() + predict() — 训练模型并预测"""
        model = RealtimePredictionModel(
            window_size=60,
            prediction_horizon=30,
            model_type="logistic",
        )

        # 训练
        model.train(mock_historical_data, mock_labels)
        assert model._model is not None
        assert len(model._feature_names) == 10

        # 预测
        current_data = list(np.random.randn(10))
        result = model.predict(current_data)

        assert "prediction" in result
        assert "probability" in result
        assert "risk_level" in result
        assert "features" in result

        # prediction 应为 0 或 1
        assert result["prediction"] in (0, 1)
        # probability 应在 [0, 1] 范围内
        assert 0.0 <= result["probability"] <= 1.0
        # risk_level 应为有效值
        assert result["risk_level"] in ("high", "medium", "low", "minimal")

    def test_extract_features(self):
        """Test 2: _extract_features — 10 维特征提取"""
        model = RealtimePredictionModel()
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        features = model._extract_features(data)

        assert isinstance(features, np.ndarray)
        assert features.shape == (10,)
        # 均值 = 5.5
        assert features[0] == pytest.approx(5.5)
        # 最小值 = 1.0
        assert features[2] == pytest.approx(1.0)
        # 最大值 = 10.0
        assert features[3] == pytest.approx(10.0)

    def test_extract_features_short_data(self):
        """Test 3: _extract_features — 短数据 (< 2 点) 返回零向量"""
        model = RealtimePredictionModel()
        features = model._extract_features([5.0])
        assert features.shape == (10,)
        assert np.all(features == 0.0)

    def test_get_risk_level(self):
        """Test 4: _get_risk_level — 风险等级判定"""
        model = RealtimePredictionModel()

        assert model._get_risk_level(0.9) == "high"
        assert model._get_risk_level(0.8) == "high"
        assert model._get_risk_level(0.6) == "medium"
        assert model._get_risk_level(0.5) == "medium"
        assert model._get_risk_level(0.4) == "low"
        assert model._get_risk_level(0.3) == "low"
        assert model._get_risk_level(0.2) == "minimal"
        assert model._get_risk_level(0.0) == "minimal"

    def test_evaluate(self, mock_historical_data, mock_labels):
        """Test 5: evaluate() — 模型评估指标"""
        model = RealtimePredictionModel(model_type="logistic")
        model.train(mock_historical_data, mock_labels)

        # 用训练数据做评估（简化测试）
        X_test = mock_historical_data.values
        y_test = mock_labels
        metrics = model.evaluate(X_test, y_test)

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "auroc" in metrics

        # 所有指标应在 [0, 1] 范围内
        for key in ["accuracy", "precision", "recall", "f1", "auroc"]:
            assert 0.0 <= metrics[key] <= 1.0, f"{key} out of range: {metrics[key]}"

    def test_model_type_switching(self, mock_historical_data, mock_labels):
        """Test 6: 模型类型切换 — logistic vs random_forest"""
        for model_type in ["logistic", "random_forest"]:
            model = RealtimePredictionModel(model_type=model_type)
            model.train(mock_historical_data, mock_labels)
            assert model._model is not None

            result = model.predict(list(np.random.randn(10)))
            assert result["prediction"] in (0, 1)

    def test_predict_before_train(self):
        """Test 7: 未训练时 predict() 抛出 RuntimeError"""
        model = RealtimePredictionModel()
        with pytest.raises(RuntimeError, match="Model not trained"):
            model.predict([1.0, 2.0, 3.0])
