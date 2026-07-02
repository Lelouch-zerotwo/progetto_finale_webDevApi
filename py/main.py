from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {"messaggio": "Server CineManiaci Attivo e Funzionante!"}