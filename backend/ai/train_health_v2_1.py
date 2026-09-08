"""Train the separate experimental V2.1 health regressor without target leakage."""
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from backend.ai.feature_engineering_v2_1 import FEATURE_COLUMNS
from backend.ai.preprocessing_v2_1 import create_run_table, load_data

MODEL_PATH=Path("models/health_estimator_v2_1.joblib")
METRICS_PATH=Path("models/health_estimator_v2_1_metrics.json")

def train_health_model():
    frame=load_data(); run_table=create_run_table(frame)
    # Reuse the classifier's stable complete-run holdout when available.
    classifier_metrics=json.loads(Path("models/fault_classifier_v2_1_metrics.json").read_text(encoding="utf-8"))
    test_runs=classifier_metrics["test_run_ids"]; train_runs=classifier_metrics["train_run_ids"]
    train=frame[frame.RunID.isin(train_runs)]; test=frame[frame.RunID.isin(test_runs)]
    model=ExtraTreesRegressor(n_estimators=250,min_samples_leaf=2,max_features=.9,random_state=42,n_jobs=-1)
    model.fit(train[FEATURE_COLUMNS],train["Health"])
    predicted=np.clip(model.predict(test[FEATURE_COLUMNS]),0,100)
    metrics={"dataset_version":"V2.1","status":"experimental","split_method":"complete RunID groups (classifier V2.1 holdout)",
             "mae":float(mean_absolute_error(test.Health,predicted)),"rmse":float(mean_squared_error(test.Health,predicted)**.5),
             "r2":float(r2_score(test.Health,predicted)),"features":FEATURE_COLUMNS,"excluded_inputs":["Health","Fault","Time","CycleCount","RunID","Step","PlannedFault","Severity","simulation metadata"],
             "train_run_ids":train_runs,"test_run_ids":test_runs,"limitation":"Synthetic simulator health target; not validated against physical wear measurements."}
    MODEL_PATH.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump({"model":model,"features":FEATURE_COLUMNS,"dataset_version":"V2.1"},MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    print(json.dumps(metrics,indent=2)); return metrics

if __name__ == "__main__": train_health_model()
