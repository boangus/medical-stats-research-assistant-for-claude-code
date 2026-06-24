"""E2E tests for realtime analytics module.

E2E-RT-01: Realtime monitoring simulation full pipeline
    (VitalSignsSimulator 60s -> monitoring report, Gate RT-1 PASS)

E2E-RT-02: Anomaly detection + alert
    (injected anomaly in simulated data -> detect anomaly, trigger alert)
"""

import sys
import time
from pathlib import Path

import numpy as np
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class TestE2ERt01MonitoringPipeline:
    """E2E-RT-01: Realtime monitoring simulation full pipeline."""

    @pytest.mark.integration
    def test_simulator_generates_stream(self):
        """Test that VitalSignsSimulator generates a valid data stream."""
        from msra_modules.realtime_analytics import VitalSignsSimulator

        # --- Arrange ---
        np.random.seed(42)
        simulator = VitalSignsSimulator()

        # --- Act: generate 60 samples (simulating 60s at 1s interval) ---
        samples = []
        for i in range(60):
            sample = simulator.generate_sample(timestamp=float(i))
            samples.append(sample)

        # --- Assert ---
        assert len(samples) == 60, "Should generate 60 samples"
        assert all(hasattr(s, "heart_rate") for s in samples)
        assert all(hasattr(s, "systolic_bp") for s in samples)
        assert all(hasattr(s, "spo2") for s in samples)

        # Values in physiological range
        hrs = [s.heart_rate for s in samples]
        assert all(20 <= hr <= 250 for hr in hrs), \
            "Heart rate should be in physiological range"

    @pytest.mark.integration
    def test_simulator_baseline_values(self):
        """Test that simulator baseline values are close to defaults."""
        from msra_modules.realtime_analytics import VitalSignsSimulator

        np.random.seed(42)
        simulator = VitalSignsSimulator()
        samples = [simulator.generate_sample(timestamp=float(i)) for i in range(100)]

        # --- Assert: mean HR close to baseline (75 ± noise) ---
        mean_hr = np.mean([s.heart_rate for s in samples])
        assert 60 <= mean_hr <= 90, f"Mean HR {mean_hr} should be near baseline 75"

        mean_spo2 = np.mean([s.spo2 for s in samples])
        assert 95 <= mean_spo2 <= 100, f"Mean SpO2 {mean_spo2} should be near baseline 98"

    @pytest.mark.integration
    def test_monitoring_report_generation(self, e2e_vitals_dataframe, e2e_output_dir):
        """Test that monitoring report can be generated from vital signs."""
        from msra_modules.realtime_analytics import ReportGenerator

        # --- Arrange ---
        df = e2e_vitals_dataframe
        report_gen = ReportGenerator()

        # Compute basic stats for the report
        stats = {}
        for col in df.columns:
            stats[col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
            }

        # --- Act ---
        report = report_gen.generate_monitoring_report(
            duration="60s",
            stats=stats,
            alerts=[],
            output_format="html",
        )

        # --- Assert ---
        assert report is not None
        assert isinstance(report, str), "Report should be a file path string"
        report_path = Path(report)
        assert report_path.exists(), "Report file should exist"
        assert report_path.stat().st_size > 0, "Report should be non-empty"

    @pytest.mark.integration
    def test_gate_rt1_passes(self):
        """Test that Gate RT-1 returns PASS for valid simulator data."""
        from msra_modules.realtime_analytics import (
            RealtimeQualityGateChecker,
            VitalSignsSimulator,
        )
        from shared.quality_gates.gate_runner import GateVerdict

        np.random.seed(42)
        simulator = VitalSignsSimulator()
        timestamps = [float(i) for i in range(60)]

        checker = RealtimeQualityGateChecker(study_id="E2E-RT-001")
        gate_result = checker.run_gate_rt1(
            source=simulator,
            timestamps=timestamps,
            detection_rate=0.05,
        )

        # --- Assert: Gate returns PASS or CONDITIONAL ---
        assert gate_result.verdict in [
            GateVerdict.PASS,
            GateVerdict.CONDITIONAL,
        ], f"Gate RT-1 should PASS or CONDITIONAL, got {gate_result.verdict}"

    @pytest.mark.integration
    def test_stream_processor_processes_vitals(self, e2e_vitals_dataframe):
        """Test that StreamProcessor can process vital signs data."""
        from msra_modules.realtime_analytics import StreamProcessor

        processor = StreamProcessor(window_size=10)
        df = e2e_vitals_dataframe

        results = []
        for _, row in df.iterrows():
            for metric in df.columns:
                event = {
                    "metric": metric,
                    "value": float(row[metric]),
                    "timestamp": float(row.name) if hasattr(row.name, '__float__') else 0.0,
                }
                result = processor.process_event(event)
                results.append(result)

        # --- Assert ---
        assert len(results) > 0, "Should process events"
        # After window fills, should have stats
        if len(results) > 10:
            last = results[-1]
            assert last is not None

    @pytest.mark.integration
    def test_vitals_reproducibility(self):
        """Test that vital signs generation is reproducible (seed=42)."""
        from tests.e2e.fixtures.generate_mock_vitals import generate_mock_vitals

        v1 = generate_mock_vitals(duration=60, interval=1.0, seed=42)
        v2 = generate_mock_vitals(duration=60, interval=1.0, seed=42)

        # --- Assert: identical ---
        for key in v1:
            np.testing.assert_array_equal(v1[key], v2[key])


class TestE2ERt02AnomalyDetection:
    """E2E-RT-02: Anomaly detection + alert."""

    @pytest.mark.integration
    def test_anomaly_injection_creates_outliers(self, e2e_vitals_dataframe_anomaly):
        """Test that anomaly injection creates detectable outliers."""
        df = e2e_vitals_dataframe_anomaly

        # --- Assert: anomalous heart rate values exist ---
        hrs = df["heart_rate"].values
        # Injected anomaly: tachycardia (140-170 bpm) in second half
        max_hr = np.max(hrs)
        assert max_hr > 130, f"Max HR {max_hr} should indicate tachycardia anomaly"

        # Check SpO2 desaturation
        spo2_vals = df["spo2"].values
        min_spo2 = np.min(spo2_vals)
        assert min_spo2 < 90, f"Min SpO2 {min_spo2} should indicate desaturation"

    @pytest.mark.integration
    def test_anomaly_detector_detects_tachycardia(self, e2e_vitals_dataframe_anomaly):
        """Test that AnomalyDetector detects tachycardia with default rules."""
        from msra_modules.realtime_analytics import AnomalyDetector

        detector = AnomalyDetector()
        detector.add_default_vital_signs_rules()

        df = e2e_vitals_dataframe_anomaly
        all_alerts = []

        for idx, row in df.iterrows():
            for metric in ["heart_rate", "systolic_bp", "spo2", "temperature"]:
                alerts = detector.evaluate(
                    metric=metric,
                    value=row[metric],
                    timestamp=float(idx),
                )
                all_alerts.extend(alerts)

        # --- Assert: at least one alert triggered ---
        assert len(all_alerts) > 0, "Should detect anomalies and trigger alerts"

        # Check alert content
        alert_metrics = [a.metric for a in all_alerts]
        assert "heart_rate" in alert_metrics or "spo2" in alert_metrics, \
            "Should detect heart rate or SpO2 anomalies"

    @pytest.mark.integration
    def test_alert_system_triggers_on_anomaly(self):
        """Test that AlertSystem triggers and records alerts."""
        from msra_modules.realtime_analytics import (
            Alert,
            AlertChannel,
            AlertSystem,
        )

        alert_system = AlertSystem()
        triggered = []

        def handler(alert):
            triggered.append(alert)

        alert_system.register_handler(AlertChannel.LOG, handler)

        # --- Act: send an alert ---
        alert = Alert(
            rule_name="tachycardia",
            metric="heart_rate",
            value=165.0,
            level="critical",
            message="Tachycardia: HR > 150 bpm",
            timestamp=time.time(),
        )
        alert_system.send_alert(alert)

        # --- Assert ---
        assert len(triggered) >= 1, "Alert handler should be called"
        assert triggered[0].rule_name == "tachycardia"

    @pytest.mark.integration
    def test_multivariate_detector_finds_anomalies(self, e2e_vitals_dataframe_anomaly):
        """Test that MultivariateDetector finds anomalies in multivariate data."""
        from msra_modules.realtime_analytics import MultivariateDetector

        detector = MultivariateDetector(contamination=0.1, random_state=42)
        df = e2e_vitals_dataframe_anomaly

        # Select numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        # Fit and detect (separate fit + detect calls)
        detector.fit(numeric_df.values, feature_names=list(numeric_df.columns))
        results = detector.detect(numeric_df.values)

        # --- Assert: some anomalies detected ---
        n_anomalies = sum(1 for r in results if r.is_anomaly)
        assert n_anomalies > 0, "Should detect at least one anomaly"

    @pytest.mark.integration
    def test_normal_data_no_false_positives(self, e2e_vitals_dataframe):
        """Test that normal data does not trigger critical alerts."""
        from msra_modules.realtime_analytics import AnomalyDetector

        detector = AnomalyDetector()
        detector.add_default_vital_signs_rules()

        df = e2e_vitals_dataframe
        critical_alerts = []

        for idx, row in df.iterrows():
            for metric in ["heart_rate", "systolic_bp", "spo2", "temperature"]:
                alerts = detector.evaluate(
                    metric=metric,
                    value=row[metric],
                    timestamp=float(idx),
                )
                critical_alerts.extend(
                    [a for a in alerts if str(a.level).endswith("CRITICAL")]
                )

        # --- Assert: minimal false positives on normal data ---
        # Normal data should not trigger critical alerts (or very few)
        assert len(critical_alerts) <= 2, \
            f"Normal data should not trigger many critical alerts, got {len(critical_alerts)}"
