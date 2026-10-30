"""PixelAI Studio inference API.

Runs a local Diffusers image model on the server. No prompt or generated media is
persisted. Video generation is explicitly unavailable until a video model adapter
and its safety controls are implemented.
"""
import base64
import hmac
import os
import threading
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="PixelAI Studio API", version="0.2.0")
_generation_lock = threading.Lock()

class GenerationRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=4000)
    output: Literal["image", "video"] = "image"
    style: Literal["Cinematografico", "Fantascienza", "Fantasy", "Animazione", "Realistico"] = "Cinematografico"
    seed: int | None = Field(default=None, ge=0, le=2147483647)

class GenerationResponse(BaseModel):
    status: str
    message: str
    mime_type: str | None = None
    image_base64: str | None = None

def verify_token(authorization: str | None) -> None:
    expected = os.getenv("PIXELAI_API_TOKEN", "")
    if len(expected) < 32:
        raise HTTPException(status_code=503, detail="API non configurata: imposta un token sicuro sul server.")
    supplied = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Autorizzazione non valida.")

@app.get("/health")
def health():
    return {
        "service": "pixelai-api",
        "api": "ready",
        "image_model": os.getenv("PIXELAI_MODEL_ID", "stabilityai/sdxl-turbo"),
        "model_load": "lazy-on-first-generation",
        "video_generation": "not-implemented",
    }

@app.post("/v1/generations", response_model=GenerationResponse)
def create_generation(
    request: GenerationRequest,
    authorization: str | None = Header(default=None),
):
    verify_token(authorization)
    if request.output == "video":
        raise HTTPException(
            status_code=501,
            detail="La generazione video non è ancora disponibile: manca un modello video e il relativo adapter."
        )

    if not _generation_lock.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Un'altra generazione è in corso. Riprova tra poco.")

    try:
        styled_prompt = f"Visual style: {request.style}. {request.prompt.strip()}"
        try:
            from model_adapter import generate_image
            png_bytes = generate_image(styled_prompt, request.seed)
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="Dipendenze IA mancanti. Installa server/requirements.txt sul server di inferenza."
            ) from exc
        except Exception as exc:
            # Do not return internal paths, credentials, or stack traces to API clients.
            raise HTTPException(
                status_code=503,
                detail="Modello non disponibile. Verifica pesi, memoria GPU e log privati del server."
            ) from exc
    finally:
        _generation_lock.release()

    if not png_bytes or len(png_bytes) > 8 * 1024 * 1024:
        raise HTTPException(status_code=502, detail="Output del modello vuoto o troppo grande.")
    return GenerationResponse(
        status="generated",
        message="Immagine generata dal modello locale.",
        mime_type="image/png",
        image_base64=base64.b64encode(png_bytes).decode("ascii"),
    )
