from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.executor import execute_tool
from app.predictor import IntentPredictor
from app.router import route_intent
from app.schemas import ExecuteRequest, ExecuteResponse, PredictResponse, RouteResponse, TextRequest


app = FastAPI(title="CampusAgent Router", description="AI Agent intent recognition and tool routing service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
predictor = IntentPredictor()


@app.get("/health")
def health():
    return {"status": "ok", "device": str(predictor.device), "model_loaded": predictor.model_loaded}


@app.post("/predict", response_model=PredictResponse)
def predict(request: TextRequest):
    try:
        return predictor.predict(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/route", response_model=RouteResponse)
def route(request: TextRequest):
    try:
        prediction = predictor.predict(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    route_info = route_intent(prediction["intent"])
    return {**prediction, **route_info}


@app.post("/execute", response_model=ExecuteResponse)
def execute(request: ExecuteRequest):
    try:
        prediction = predictor.predict(request.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    route_info = route_intent(prediction["intent"])
    execution = execute_tool(prediction["intent"], request.text, request.context or "")
    return {**prediction, **route_info, **execution}
