from fastapi import APIRouter, Query, Request
from backend.api.schemas import BatchPredictionRequest, PredictionRequest

router = APIRouter()

@router.post("/predict")
def predict(body: PredictionRequest, request: Request): return request.app.state.backend.predict(body.session_id, body.reading)

@router.post("/predict/batch")
def predict_batch(body: BatchPredictionRequest, request: Request):
    service = request.app.state.backend
    if body.reset_buffer: service.reset_buffer(body.session_id)
    return {"session_id":body.session_id, "predictions":[service.predict(body.session_id, item) for item in body.readings]}

@router.get("/history")
def history(request: Request, session_id: str | None = None, limit: int = Query(100, ge=1, le=1000)):
    return {"items":request.app.state.backend.repository.history(session_id, limit), "limit":limit}
