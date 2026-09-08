import json
from fastapi import APIRouter, Request
from backend.ai.feature_engineering_v2_1 import BASE_FEATURES, FEATURE_COLUMNS

router = APIRouter()

@router.get("/health")
def health(request: Request):
    service=request.app.state.backend
    return {"status":"ok" if service.model.bundle else "degraded", "classifier_available":service.model.bundle is not None,
            "health_model_available":service.model.health_bundle is not None,"database_available":service.repository.ping(),"simulator_status":"available"}

@router.get("/model/info")
def model_info(request: Request):
    service=request.app.state.backend
    metrics = json.loads(service.settings.classifier_metrics_path.read_text(encoding="utf-8"))
    cv = json.loads(service.settings.classifier_cv_metrics_path.read_text(encoding="utf-8"))
    health_metrics = json.loads(service.settings.health_metrics_path.read_text(encoding="utf-8")) if service.settings.health_metrics_path.exists() else None
    return {"model_version":"V2.1", "supported_faults":metrics["class_names"], "required_raw_sensors":BASE_FEATURES,
            "feature_names":FEATURE_COLUMNS,"evaluation_metrics":{"holdout":{k:metrics[k] for k in ("accuracy","balanced_accuracy","macro_f1")},
            "five_fold":{"accuracy_mean":cv["accuracy_mean"],"accuracy_std":cv["accuracy_std"]},"health":health_metrics},
            "limitations":["Trained only on synthetic V2.1 simulation data.","Not validated for physical equipment or safety control.","RUL is a transparent trend estimate, not a validated AI failure-time model."]}
