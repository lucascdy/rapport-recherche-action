"""
Serveur relais pour le Générateur de Rapport de Recherche Action.

Sert la page (index.html) et relaie les requêtes de génération vers l'API
Anthropic avec la clé stockée côté serveur (variable ANTHROPIC_API_KEY) —
la clé n'est jamais exposée au navigateur.

Lancement local :  uvicorn server:app --reload
"""

import os
import time
from collections import defaultdict, deque

import anthropic
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

MODEL_ID = "claude-sonnet-4-6"
MAX_TOKENS = 9000

# Limite anti-abus : 10 générations par heure et par adresse IP
RATE_LIMIT = 10
RATE_WINDOW_S = 3600

app = FastAPI(docs_url=None, redoc_url=None)
client = anthropic.Anthropic()

_hits: dict[str, deque] = defaultdict(deque)


class GenerateRequest(BaseModel):
    system: str = Field(max_length=8_000)
    user: str = Field(max_length=30_000)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.get("/")
def index():
    return FileResponse("index.html", media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate")
def generate(req: GenerateRequest, request: Request):
    ip = _client_ip(request)
    now = time.time()
    hits = _hits[ip]
    while hits and now - hits[0] > RATE_WINDOW_S:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Limite atteinte : {RATE_LIMIT} rapports par heure. Réessayez plus tard.",
        )
    hits.append(now)

    # La requête Anthropic part ici (avant le début du stream HTTP) pour que
    # les erreurs API (401, 429, 529…) remontent au navigateur avec leur vrai
    # code — le front s'appuie dessus pour son mécanisme de retry.
    stream_mgr = client.messages.stream(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=req.system,
        messages=[{"role": "user", "content": req.user}],
    )
    try:
        stream = stream_mgr.__enter__()
    except anthropic.APIStatusError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except anthropic.APIConnectionError:
        raise HTTPException(status_code=502, detail="Impossible de joindre l'API Anthropic.")

    def stream_text():
        # Streaming : la réponse commence immédiatement, ce qui évite les
        # timeouts du proxy Render sur les générations longues (1-2 min).
        try:
            for text in stream.text_stream:
                yield text
        finally:
            stream_mgr.__exit__(None, None, None)

    return StreamingResponse(stream_text(), media_type="text/plain; charset=utf-8")
