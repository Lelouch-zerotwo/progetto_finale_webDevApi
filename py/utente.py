from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .classi_validazione import UtenteAuth
import sqlite3
import hashlib
import secrets

router = APIRouter()

# Inizializziamo lo schema di sicurezza di FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def calcola_hash(password_chiaro: str) -> str:
    return hashlib.sha256(password_chiaro.encode('utf-8')).hexdigest()

@router.post("/register")
def registra_utente(dati: UtenteAuth):
    password_sicura = calcola_hash(dati.password)
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO utenti (username, password_hash) VALUES (?, ?)", (dati.username, password_sicura))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Questo username è già occupato.")
    finally:
        conn.close()
    return {"status": "Utente registrato con successo!"}

@router.post("/login")
def login_utente(dati: UtenteAuth):
    hash_da_verificare = calcola_hash(dati.password)
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM utenti WHERE username = ?", (dati.username,))
    utente = cursor.fetchone()
    
    if utente is None or utente[1] != hash_da_verificare:
        conn.close()
        raise HTTPException(status_code=401, detail="Credenziali non valide.")
    
    token_sessione = secrets.token_hex(16)
    cursor.execute("""
        UPDATE utenti 
        SET token = ?, token_scadenza = datetime('now', '+1 day') 
        WHERE id = ?
    """, (token_sessione, utente[0]))
    conn.commit()
    conn.close()
    return {"status": "Login effettuato con successo", "token": token_sessione}

# Applichiamo Depends(oauth2_scheme) per estrarre il token dall'Header
@router.get("/profilo")
def mostra_profilo_utente(token: str = Depends(oauth2_scheme)):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, token_scadenza FROM utenti WHERE token = ?", (token,))
    utente_trovato = cursor.fetchone()
    conn.close()
    
    if utente_trovato is None:
        raise HTTPException(status_code=401, detail="Sessione non valida.")
        
    return {
        "utente_id": utente_trovato["id"], 
        "username": utente_trovato["username"],
        "scadenza": utente_trovato["token_scadenza"]
    }