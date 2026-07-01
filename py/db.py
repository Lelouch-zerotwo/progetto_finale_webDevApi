import sqlite3

def dbinit():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # 1. Tabella Film [cite: 9, 14]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS film (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT NOT NULL,
            trama TEXT,
            anno INTEGER,
            url_locandina TEXT,
            tmdb_id TEXT
        )
    """)
    
    # 2. Tabella Utenti (con colonna token per gestire le sessioni) [cite: 126, 130]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            token TEXT
        )
    """)

    # 3. Tabella Playlist_Video [cite: 106, 108]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_video (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo_playlist TEXT NOT NULL,
            utente_id INTEGER NOT NULL,
            film_id INTEGER,
            FOREIGN KEY (utente_id) REFERENCES utenti (id),
            FOREIGN KEY (film_id) REFERENCES film (id)
        )
    """)
    
    # 4. Tabella Elementi_Video (Commenti e Link YouTube) [cite: 9, 14, 15]
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS elementi_video (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id INTEGER NOT NULL,
            url_video_youtube TEXT NOT NULL,
            commento TEXT,
            FOREIGN KEY (film_id) REFERENCES film (id)
        )
    """)
    conn.commit()

    # Popolamento iniziale se la tabella film è vuota
    cursor.execute("SELECT COUNT(*) FROM film")
    count = cursor.fetchone()[0]

    if count == 0:
        film_esempi = [
            ("Inception", "Un ladro che ruba segreti aziendali attraverso l'uso della tecnologia di condivisione dei sogni...", 2010, "https://www.themoviedb.org/t/p/w600_and_h900_face/5QHWgqaBxZI1eM5e3YhyKzY5o3z.jpg", "27205"),
            ("The Matrix", "Un hacker scopre da misteriosi ribelli la vera natura della sua realtà...", 1999, "https://www.themoviedb.org/t/p/w600_and_h900_face/yQZX4scmfYtj4ccKFNGZJlOj1y9.jpg", "603"),
            ("Interstellar", "Un gruppo di esploratori viaggia attraverso un wormhole nello spazio...", 2014, "https://www.themoviedb.org/t/p/w600_and_h900_face/bMKiLh0mES4Uiococ240lbbTGXQ.jpg", "157336")
        ]
        cursor.executemany("""
            INSERT INTO film (titolo, trama, anno, url_locandina, tmdb_id) 
            VALUES (?, ?, ?, ?, ?)
        """, film_esempi)    
        conn.commit()

    conn.close()
    print("Database inizializzato correttamente!")