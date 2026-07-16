from pydantic import BaseModel

# Modello per l'autenticazione utente (Registrazione e Login)
class UtenteAuth(BaseModel):
    username: str
    password: str

# Modello per l'inserimento manuale o automatico di un film
class FilmIn(BaseModel):
    titolo: str 
    trama: str 
    anno: int 
    url_locandina: str 
    url_video_youtube: str
    tmdb_id: str  # Gestito come stringa coerentemente con il DB

# Modello per la creazione di una nuova playlist 
class PlaylistIn(BaseModel):
    titolo_playlist: str

# Modello per l'aggiunta di un commento/video YouTube a un film
class CommentoIn(BaseModel):
    commento: str