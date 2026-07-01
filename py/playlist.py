from fastapi import APIRouter, HTTPException
from classi_validazione import PlaylistIn
import sqlite3

router = APIRouter()

# Crea una nuova testa di playlist (film_id inizialmente NULL) 
@router.post("/playlist")
def crea_playlist(dati: PlaylistIn, token: str): 
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Trova l'utente tramite token [cite: 126, 130]
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone() 
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Devi fare il login per creare una playlist!") 
        
    id_utente = utente[0] 
    
    # Inseriamo il record radice della playlist 
    cursor.execute("""
        INSERT INTO playlist_video (titolo_playlist, utente_id, film_id) 
        VALUES (?, ?, NULL)
    """, (dati.titolo_playlist, id_utente))
    
    conn.commit()
    conn.close()
    return {"status": "Playlist creata con successo!"}

# Restituisce solo le playlist uniche dell'utente loggato 
@router.get("/playlist")
def dammi_mie_playlist(token: str): 
    if not token:
        raise HTTPException(status_code=401, detail="Token mancante.") 
        
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone() 
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Token non valido.") 
        
    # Seleziona i titoli univoci escludendo le righe di inserimento film dirette 
    cursor.execute("""
        SELECT DISTINCT titolo_playlist 
        FROM playlist_video 
        WHERE utente_id = ?
    """, (utente[0],))
    
    mie_liste = cursor.fetchall()
    conn.close()
    return [dict(r) for r in mie_liste]

# Aggiunge un film ad una playlist esistente 
@router.post("/playlist/aggiungi-film")
def aggiungi_film_a_lista(titolo_p: str, id_f: int, token: str): 
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone() 
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Azione non autorizzata.")
        
    # Inserisce una nuova riga relazionale che lega titolo, utente e film specifico [cite: 161, 168, 169]
    cursor.execute("""
        INSERT INTO playlist_video (titolo_playlist, utente_id, film_id)
        VALUES (?, ?, ?)
    """, (titolo_p, utente[0], id_f))
    
    conn.commit()
    conn.close()
    return {"status": "Film aggiunto alla playlist!"}

# Ottiene i dettagli dei film dentro una specifica playlist tramite JOIN 
@router.get("/playlist/dettaglio")
def dettaglio_playlist(titolo: str, token: str): 
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM utenti WHERE token = ?", (token,))
    utente = cursor.fetchone()
    if utente is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Effettua il login per vedere il dettaglio.")
        
    # Esegue la query JOIN per estrarre le info dei film associati a questa lista 
    cursor.execute("""
        SELECT film.id, film.titolo, film.anno, film.url_locandina 
        FROM playlist_video 
        JOIN film ON playlist_video.film_id = film.id 
        WHERE playlist_video.titolo_playlist = ? AND playlist_video.utente_id = ?
    """, (titolo, utente[0]))
    
    film_in_playlist = cursor.fetchall()
    conn.close()
    return [dict(f) for f in film_in_playlist]