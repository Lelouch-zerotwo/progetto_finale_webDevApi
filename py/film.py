from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .classi_validazione import FilmIn, CommentoIn
import sqlite3

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.get("/film")
def lista_film():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM film")
    risultati = cursor.fetchall()
    conn.close()
    return [dict(r) for r in risultati]

@router.get("/film/cerca")
def cerca_film(keyword: str):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM film WHERE titolo LIKE ?", (f"%{keyword}%",))
    risultati = cursor.fetchall()
    conn.close()
    return [dict(r) for r in risultati]

@router.get("/film/{id_film}")
def dettaglio_film(id_film: int):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM film WHERE id = ?", (id_film,))
    film = cursor.fetchone() 
    
    if film is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Film non trovato")
        
    cursor.execute("""
        SELECT c.testo, c.data_commento, u.username 
        FROM commenti c
        JOIN utenti u ON c.utente_id = u.id
        WHERE c.film_id = ?
        ORDER BY c.data_commento DESC
    """, (id_film,))
    elementi = cursor.fetchall()
    
    conn.close()
    return {
        "film": dict(film),
        "commenti": [dict(e) for e in elementi]
    }

@router.post("/film")
def aggiungi_film_manuale(dati: FilmIn, token: str = Depends(oauth2_scheme)):
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone()
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Operazione non autorizzata. Effettua il login.")
        
    cursor.execute("""
        INSERT INTO film (titolo, trama, anno, url_locandina, url_trailer, tmdb_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dati.titolo, dati.trama, dati.anno, dati.url_locandina, dati.url_trailer, dati.tmdb_id))
    
    conn.commit()
    conn.close()
    return {"status": "Film inserito con successo!"}

@router.post("/film/{id_film}/commento")
def aggiungi_commento(id_film: int, dati: CommentoIn, token: str = Depends(oauth2_scheme)):
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone()
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Devi essere loggato per lasciare un commento.")
        
    cursor.execute("""
        INSERT INTO commenti (film_id, utente_id, testo)
        VALUES (?, ?, ?)
    """, (id_film, utente[0], dati.testo))
    
    conn.commit()
    conn.close()
    return {"status": "Commento aggiunto!"}