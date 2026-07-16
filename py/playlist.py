from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .classi_validazione import PlaylistIn
import sqlite3

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/playlist")
def crea_playlist(dati: PlaylistIn, token: str = Depends(oauth2_scheme)): 
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone() 
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Devi fare il login per creare una playlist!") 
        
    cursor.execute("""
        INSERT INTO playlist (titolo, utente_id) 
        VALUES (?, ?)
    """, (dati.titolo, utente[0]))
    
    conn.commit()
    conn.close()
    return {"status": "Playlist creata con successo!"}

@router.get("/playlist")
def dammi_mie_playlist(token: str = Depends(oauth2_scheme)): 
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone() 
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Token non valido.") 
        
    cursor.execute("""
        SELECT id, titolo, data_creazione
        FROM playlist 
        WHERE utente_id = ?
        ORDER BY data_creazione DESC
    """, (utente[0],))
    
    mie_liste = cursor.fetchall()
    conn.close()
    return [dict(r) for r in mie_liste]

@router.post("/playlist/aggiungi-film")
def aggiungi_film_a_lista(titolo_p: str, id_f: int, token: str = Depends(oauth2_scheme)): 
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone() 
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Azione non autorizzata.")
        
    cursor.execute("SELECT id FROM playlist WHERE titolo = ? AND utente_id = ?", (titolo_p, utente[0]))
    playlist = cursor.fetchone()
    if playlist is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Playlist non trovata.")
        
    cursor.execute("""
        INSERT INTO playlist_film (playlist_id, film_id)
        VALUES (?, ?)
    """, (playlist[0], id_f))
    
    conn.commit()
    conn.close()
    return {"status": "Film aggiunto alla playlist!"}

@router.get("/playlist/dettaglio")
def dettaglio_playlist(titolo: str, token: str = Depends(oauth2_scheme)): 
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone()
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Effettua il login per vedere il dettaglio.")
        
    cursor.execute("""
        SELECT f.id, f.titolo, f.anno, f.url_locandina 
        FROM playlist_film pf 
        JOIN film f ON pf.film_id = f.id 
        JOIN playlist p ON pf.playlist_id = p.id
        WHERE p.titolo = ? AND p.utente_id = ?
    """, (titolo, utente[0]))
    
    film_in_playlist = cursor.fetchall()
    conn.close()
    return [dict(f) for f in film_in_playlist]