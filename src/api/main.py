from collections.abc import Callable

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.api.schemas import PredictRequest, PredictResponse
from src.infrastructure.db import init_db, save_prediction
from src.infrastructure.model_runtime import ModelRuntime
from src.infrastructure.settings import get_settings, validate_required_settings

app = FastAPI(title="Wafer Project API", version="1.0.0")


@app.middleware("http")
async def enforce_request_size(request: Request, call_next: Callable):
    settings = get_settings()
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.request_limit_bytes:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Payload exceeds 1MB limit."},
        )
    return await call_next(request)


def verify_api_key(x_api_key: str = Header(default="")) -> None:
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@app.on_event("startup")
def startup_event() -> None:
    validate_required_settings()
    init_db()
    app.state.runtime = ModelRuntime()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    runtime = getattr(app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Runtime not ready")
    return {"status": "ready"}


@app.post("/predict", response_model=PredictResponse, dependencies=[Depends(verify_api_key)])
def predict(payload: PredictRequest) -> PredictResponse:
    runtime: ModelRuntime = app.state.runtime
    result = runtime.predict(payload.sensors)

    save_prediction(
        payload={"sensors": payload.sensors},
        label=result.label,
        confidence=result.confidence,
        raw_prediction=result.raw_prediction,
        source="api",
    )

    return PredictResponse(label=result.label, confidence=result.confidence)
