from fastapi import APIRouter, HTTPException, Query
from .classi_validazione import FilmIn, ElementoVideoIn
import sqlite3

router = APIRouter()

# Ritorna la lista di tutti i film
@router.get("/film")
def lista_film():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM film")
    risultati = cursor.fetchall() # Corretto fetchall() per avere una lista completa
    conn.close()
    return [dict(r) for r in risultati]

# Rotta di ricerca parziale tramite operatore LIKE 
@router.get("/film/cerca")
def cerca_film(keyword: str):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM film WHERE titolo LIKE ?", (f"%{keyword}%",))
    risultati = cursor.fetchall() # Otteniamo tutti i film corrispondenti 
    conn.close()
    return [dict(r) for r in risultati]

# Rotta di dettaglio del film per ID 
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
        
    # Recuperiamo anche i video/commenti associati a questo film 
    cursor.execute("SELECT url_video_youtube, commento FROM elementi_video WHERE film_id = ?", (id_film,))
    elementi = cursor.fetchall()
    
    conn.close()
    return {
        "film": dict(film),
        "commenti": [dict(e) for e in elementi]
    }

# Permette l'inserimento manuale di un film (Solo Utenti Loggati)
@router.post("/film")
def aggiungi_film_manuale(dati: FilmIn, token: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Controllo validità token 
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone()
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Operazione non autorizzata. Effettua il login.")
        
    cursor.execute("""
        INSERT INTO film (titolo, trama, anno, url_locandina, tmdb_id)
        VALUES (?, ?, ?, ?, ?)
    """, (dati.titolo, dati.trama, dati.anno, dati.url_locandina, dati.tmdb_id))
    
    conn.commit()
    conn.close()
    return {"status": "Film inserito con successo!"}

# Inserimento di commenti/video YouTube (Solo Utenti Loggati)
@router.post("/film/{id_film}/commento")
def aggiungi_commento_video(id_film: int, dati: ElementoVideoIn, token: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Verifica autenticazione 
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Devi essere loggato per lasciare un commento.")
        
    cursor.execute("""
        INSERT INTO elementi_video (film_id, url_video_youtube, commento)
        VALUES (?, ?, ?)
    """, (id_film, dati.url_video_youtube, dati.commento))
    
    conn.commit()
    conn.close()
    return {"status": "Commento e video aggiunti!"}