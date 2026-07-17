from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .db import dbinit
from .film import router as film_router
from .utente import router as utente_router
from .playlist import router as playlist_router

# Inizializzazione fisica del DB SQLite
dbinit()

app = FastAPI(title="CineManiaci API")

# Abilitazione CORS per permettere lo scambio dati tra le pagine HTML locali e FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrazione dei moduli delle rotte
app.include_router(film_router)
app.include_router(utente_router)
app.include_router(playlist_router)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "www"


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/html/catalogo.html")


# Servizio dei file frontend sulla stessa porta 8000
#app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
#app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")
#app.mount("/html", StaticFiles(directory=STATIC_DIR / "html"), name="html")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
