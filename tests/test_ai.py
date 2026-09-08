import pandas as pd
import pytest
from backend.ai.feature_engineering_v2_1 import BASE_FEATURES, FEATURE_COLUMNS, OnlineFeatureBuffer, add_temporal_features
from backend.ai.services import ModelArtifactError, ModelService, RulEstimator, control_recommendation
from backend.api.schemas import SensorReading

LEAKAGE={"Time","CycleCount","Health","Fault","RunID","Step","PlannedFault","Severity"}

def rows():
    return [{"Pressure":5+i*.01,"Temperature":30+i*.1,"Position":float((i%10)*10),"Flow":10+i*.02,"Speed":120-i*.1,"Vibration":.3+i*.01,"Load":15+i*.2} for i in range(15)]

def test_online_offline_parity_order_and_no_leakage():
    data=rows(); frame=pd.DataFrame(data); frame["RunID"]="x"; frame["Step"]=range(len(frame))
    expected=add_temporal_features(frame).iloc[-1][FEATURE_COLUMNS]
    buffer=OnlineFeatureBuffer(50)
    for row in data: actual,warmup=buffer.add("x",row)
    assert list(actual)==FEATURE_COLUMNS and not (set(FEATURE_COLUMNS)&LEAKAGE)
    assert actual==pytest.approx(expected.to_dict()) and warmup is False

def test_independent_buffers_and_reset():
    buffer=OnlineFeatureBuffer(11); buffer.add("a",rows()[0]); buffer.add("a",rows()[1]); buffer.add("b",rows()[0])
    assert buffer.size("a")==2 and buffer.size("b")==1
    buffer.reset("a"); assert buffer.size("a")==0 and buffer.size("b")==1

def test_model_feature_order_and_missing_error(tmp_path):
    service=ModelService("models/fault_classifier_v2_1.joblib","models/health_estimator_v2_1.joblib"); service.load()
    assert list(service.bundle["features"])==FEATURE_COLUMNS
    with pytest.raises(ModelArtifactError): ModelService(tmp_path/"missing.joblib").load()

def test_rul_is_honest_when_history_insufficient():
    result=RulEstimator().update("x",90,1); assert result["estimated_remaining_cycles"] is None and result["status"]=="insufficient_history"

@pytest.mark.parametrize("fault",["Healthy","Air Leakage","Pressure Drop","Seal Wear","Valve Sticking"])
def test_control_policy_for_each_fault(fault):
    reading=SensorReading(pressure=5,temperature=30,position=0,flow=10,speed=120,vibration=.4,load=15)
    rul=RulEstimator().update("x",90,1)
    result=control_recommendation(fault,.9,90,reading,rul)
    assert result["output_type"]=="advisory_simulation" and result["inspection_action"]
