import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.config.settings import settings

READING={"pressure":5.4,"temperature":31,"position":10,"flow":10,"speed":122,"vibration":.4,"load":15,"cycle_count":1}

@pytest.fixture()
def client(tmp_path):
    old=settings.database_path; settings.database_path=tmp_path/"test.db"; settings.websocket_interval=.001
    with TestClient(app) as value: yield value
    settings.database_path=old

def test_root_health_and_model_info(client):
    assert client.get("/").status_code==200
    assert client.get("/docs").status_code==200 and client.get("/openapi.json").status_code==200
    health=client.get("/api/v1/health").json(); assert health["classifier_available"] and health["database_available"]
    info=client.get("/api/v1/model/info").json(); assert len(info["feature_names"])==23 and "Health" not in info["feature_names"]

def test_prediction_validation_batch_and_history(client):
    response=client.post("/api/v1/predict",json={"session_id":"c1","reading":READING})
    assert response.status_code==200; body=response.json(); assert body["warmup"] and abs(sum(body["probabilities"].values())-1)<1e-8
    assert 0<=body["health"]<=100 and body["control"]["output_type"]=="advisory_simulation"
    assert client.post("/api/v1/predict",json={"session_id":"c1","reading":{**READING,"pressure":99}}).status_code==422
    batch=client.post("/api/v1/predict/batch",json={"session_id":"c2","readings":[READING,{**READING,"position":20}]}).json()
    assert [x["buffer_samples"] for x in batch["predictions"]]==[1,2]
    history=client.get("/api/v1/history",params={"session_id":"c2","limit":10}).json()["items"]
    assert len(history)==2 and all(x["session_id"]=="c2" for x in history)

def test_simulation_lifecycle(client):
    created=client.post("/api/v1/simulations",json={"session_id":"sim","planned_fault":"Air Leakage","seed":7}).json()
    assert created["step"]==0 and created["simulation_metadata"]["PlannedFault"]=="Air Leakage"
    stepped=client.post("/api/v1/simulations/sim/step").json(); assert stepped["step"]==1 and stepped["prediction"]
    assert client.post("/api/v1/simulations/sim/stop").json()["running"] is False
    assert client.delete("/api/v1/simulations/sim").json()["status"]=="reset"
    assert client.get("/api/v1/simulations/sim").status_code==404

def test_websocket_smoke(client):
    client.post("/api/v1/simulations",json={"session_id":"ws","seed":1})
    with client.websocket_connect("/api/v1/ws/simulations/ws") as socket:
        message=socket.receive_json(); assert message["type"]=="simulation_update" and message["data"]["prediction"]
