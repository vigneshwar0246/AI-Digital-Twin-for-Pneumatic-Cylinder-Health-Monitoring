"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.ai.feature_engineering_v2_1 import OnlineFeatureBuffer
from backend.ai.services import ModelArtifactError, ModelService, RulEstimator, control_recommendation
from backend.config.settings import settings
from backend.database.database import PredictionRepository
from backend.simulator.service_v2_1 import SimulationService
from backend.api.routes import health, prediction, simulation

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log=logging.getLogger(__name__)

class BackendService:
    def __init__(self, config=settings):
        self.settings=config; self.model=ModelService(config.classifier_path,config.health_model_path)
        self.features=OnlineFeatureBuffer(config.buffer_size); self.rul=RulEstimator(config.critical_health,config.max_rul_cycles)
        self.repository=PredictionRepository(config.database_path); self.simulations=SimulationService()
    def start(self): self.repository.initialize(); self.model.load()
    def reset_buffer(self, session_id): self.features.reset(session_id); self.rul.reset(session_id)
    def predict(self,session_id,reading):
        features,warmup=self.features.add(session_id,reading.feature_dict())
        fault,confidence,probabilities,health_value=self.model.predict(features)
        rul=self.rul.update(session_id,health_value,reading.cycle_count)
        control=control_recommendation(fault,confidence,health_value,reading,rul)
        result={"timestamp":datetime.now(timezone.utc).isoformat(),"session_id":session_id,"reading":reading.model_dump(),
                "fault":fault,"confidence":confidence,"probabilities":probabilities,"health":health_value,"health_status":"experimental" if health_value is not None else "unavailable",
                "rul":rul,"control":control,"warmup":warmup,"buffer_samples":self.features.size(session_id)}
        result["history_id"]=self.repository.add(result); return result

@asynccontextmanager
async def lifespan(app):
    app.state.backend=BackendService(); app.state.backend.start(); log.info("Backend services initialized")
    yield

app=FastAPI(title=settings.app_name,version=settings.version,lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(health.router,prefix="/api/v1",tags=["service"]); app.include_router(prediction.router,prefix="/api/v1",tags=["prediction"]); app.include_router(simulation.router,prefix="/api/v1",tags=["simulation"])

@app.get("/")
def root(): return {"application":settings.app_name,"version":settings.version,"status":"ok","documentation_url":"/docs"}

@app.exception_handler(RequestValidationError)
async def validation_error(request:Request, exc): return JSONResponse(status_code=422,content={"error":{"code":"validation_error","message":"Request validation failed","details":exc.errors()}})
@app.exception_handler(ModelArtifactError)
async def model_error(request:Request, exc): return JSONResponse(status_code=503,content={"error":{"code":"model_unavailable","message":str(exc)}})
@app.exception_handler(KeyError)
async def missing_error(request:Request, exc): return JSONResponse(status_code=404,content={"error":{"code":"not_found","message":str(exc.args[0])}})
@app.exception_handler(ValueError)
async def value_error(request:Request, exc): return JSONResponse(status_code=409,content={"error":{"code":"invalid_state","message":str(exc)}})
