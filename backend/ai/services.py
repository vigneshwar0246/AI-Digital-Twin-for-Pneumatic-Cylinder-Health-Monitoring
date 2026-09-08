"""Inference, experimental health/RUL, and advisory-control services."""
import json
from collections import defaultdict, deque
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from backend.ai.feature_engineering_v2_1 import FEATURE_COLUMNS


class ModelArtifactError(RuntimeError): pass


class ModelService:
    def __init__(self, classifier_path, health_path=None):
        self.classifier_path, self.health_path = Path(classifier_path), Path(health_path) if health_path else None
        self.bundle = self.health_bundle = None

    def load(self):
        if not self.classifier_path.exists(): raise ModelArtifactError(f"Classifier artifact not found: {self.classifier_path}")
        bundle = joblib.load(self.classifier_path)
        if list(bundle.get("features", [])) != FEATURE_COLUMNS: raise ModelArtifactError("Classifier feature ordering is incompatible with V2.1")
        self.bundle = bundle
        if self.health_path and self.health_path.exists():
            health = joblib.load(self.health_path)
            if list(health.get("features", [])) != FEATURE_COLUMNS: raise ModelArtifactError("Health model feature ordering is incompatible with V2.1")
            self.health_bundle = health

    def predict(self, features):
        if self.bundle is None: raise ModelArtifactError("Classifier is unavailable")
        frame = pd.DataFrame([[features[x] for x in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        scaled = self.bundle["scaler"].transform(frame)
        probabilities = self.bundle["model"].predict_proba(scaled)[0]
        classes = self.bundle["label_encoder"].inverse_transform(self.bundle["model"].classes_)
        result = {str(k): float(v) for k, v in zip(classes, probabilities)}
        fault = max(result, key=result.get)
        health = None
        if self.health_bundle:
            health = float(np.clip(self.health_bundle["model"].predict(frame)[0], 0, 100))
        return fault, result[fault], result, health


class RulEstimator:
    def __init__(self, critical_health=30, max_cycles=10000, history=30):
        self.critical, self.cap = critical_health, max_cycles
        self.values = defaultdict(lambda: deque(maxlen=history))

    def update(self, session_id, health, cycle_count=None):
        if health is None: return self._result(None, "health_unavailable", "Health model is unavailable.", "none")
        x = float(cycle_count) if cycle_count is not None else float(len(self.values[session_id]))
        self.values[session_id].append((x, float(health)))
        points = self.values[session_id]
        if len(points) < 5 or len({p[0] for p in points}) < 2:
            return self._result(None, "insufficient_history", "At least five observations across changing cycles/steps are required.", "low")
        slope = float(np.polyfit([p[0] for p in points], [p[1] for p in points], 1)[0])
        if slope >= -1e-6:
            return self._result(None, "non_degrading_trend", "No positive degradation rate is available; no RUL is invented.", "low")
        estimate = min(self.cap, max(0, int(round((health-self.critical)/-slope))))
        return self._result(estimate, "estimated", "Linear trend of recent predicted health; prototype only.", "medium" if len(points) >= 10 else "low")

    def _result(self, value, status, explanation, reliability):
        return {"estimated_remaining_cycles": value, "status": status, "method": "recent_health_linear_trend", "reliability": reliability,
                "critical_health_threshold": self.critical, "explanation": explanation}

    def reset(self, session_id): self.values.pop(session_id, None)


def control_recommendation(fault, confidence, health, reading, rul):
    policies = {
        "Healthy": ("standard", "routine", 100, 100, "Continue routine monitoring."),
        "Air Leakage": ("efficiency_limited", "planned", 90, 90, "Inspect hoses, fittings, seals, and air consumption."),
        "Pressure Drop": ("load_limited", "urgent", 80, 75, "Check supply pressure, regulator, restrictions, and load."),
        "Seal Wear": ("reduced_stress", "planned", 75, 75, "Inspect and replace seals; check lubrication."),
        "Valve Sticking": ("restricted", "urgent", 65, 70, "Inspect valve/spool and contamination before continued duty."),
    }
    mode, priority, speed, load, action = policies[fault]
    shutdown = bool((health is not None and health <= 30) or reading.pressure > 10 or reading.temperature > 90 or reading.vibration > 10 or rul["status"] == "estimated" and rul["estimated_remaining_cycles"] == 0)
    if confidence < .60:
        mode, priority, speed, load, action = "observe", "observation", 90, 90, "Collect additional observations and request human review."
    return {"output_type":"advisory_simulation", "operating_mode":mode, "maintenance_priority":priority,
            "recommended_speed_limit_percent":speed, "recommended_load_limit_percent":load,
            "inspection_action":action, "shutdown_recommended":shutdown,
            "reason": "Safety boundary exceeded." if shutdown else f"Policy for {fault} at {confidence:.1%} confidence. No physical command was sent."}
