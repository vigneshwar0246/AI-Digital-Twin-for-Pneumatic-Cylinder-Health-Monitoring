from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from backend.api.schemas import SimulationCreateRequest, SensorReading

router=APIRouter()

@router.post("/simulations", status_code=201)
def create(body:SimulationCreateRequest, request:Request):
    backend=request.app.state.backend; backend.reset_buffer(body.session_id)
    return backend.simulations.create(body.session_id, body.planned_fault, body.seed, fault_start=body.fault_start,
                                      maximum_severity=body.maximum_severity, rise_time=body.rise_time)

@router.get("/simulations/{session_id}")
def state(session_id:str, request:Request): return request.app.state.backend.simulations.state(session_id)

@router.post("/simulations/{session_id}/step")
def step(session_id:str, request:Request):
    backend=request.app.state.backend; result=backend.simulations.advance(session_id)
    raw=result["true_simulated_state"]
    reading=SensorReading(**{k.lower():raw[k] for k in ("Pressure","Temperature","Position","Flow","Speed","Vibration","Load")}, cycle_count=raw["CycleCount"])
    prediction=backend.predict(session_id,reading); backend.simulations.sessions[session_id].last_prediction=prediction
    result["prediction"]=prediction; return result

@router.post("/simulations/{session_id}/stop")
def stop(session_id:str, request:Request): return request.app.state.backend.simulations.stop(session_id)

@router.delete("/simulations/{session_id}")
def reset(session_id:str, request:Request):
    backend=request.app.state.backend; backend.simulations.reset(session_id); backend.reset_buffer(session_id)
    return {"session_id":session_id,"status":"reset"}

@router.websocket("/ws/simulations/{session_id}")
async def stream(websocket:WebSocket, session_id:str):
    await websocket.accept(); backend=websocket.app.state.backend
    try:
        while backend.simulations.state(session_id)["running"]:
            result=backend.simulations.advance(session_id); raw=result["true_simulated_state"]
            reading=SensorReading(**{k.lower():raw[k] for k in ("Pressure","Temperature","Position","Flow","Speed","Vibration","Load")},cycle_count=raw["CycleCount"])
            result["prediction"]=backend.predict(session_id,reading)
            await websocket.send_json({"type":"simulation_update","data":result})
            import asyncio; await asyncio.sleep(backend.settings.websocket_interval)
    except (WebSocketDisconnect, KeyError, ValueError): pass
