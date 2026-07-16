import sqlite3

def dbinit():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # IMPORTANTE: Abilita il supporto alle chiavi esterne in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Tabella Film
    # Ho aggiunto la colonna "url_trailer" per memorizzare il trailer di YouTube direttamente legato al film
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS film (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo TEXT NOT NULL,
            trama TEXT,
            anno INTEGER,
            url_locandina TEXT,
            url_video_youtube TEXT, 
            tmdb_id TEXT
        )
    """)
    
    # 2. Tabella Utenti
    # Aggiunto 'token_scadenza' per la sicurezza e 'data_registrazione' come timestamp utile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            token TEXT,
            token_scadenza DATETIME,
            data_registrazione DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Tabella Playlist (Contenitore principale)
    # Definisce solo il nome della playlist e chi l'ha creata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titolo_playlist TEXT NOT NULL,
            utente_id INTEGER NOT NULL,
            data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utente_id) REFERENCES utenti (id) ON DELETE CASCADE
        )
    """)
    
    # 4. Tabella Playlist_Film (Tabella di collegamento molti-a-molti)
    # Associa i film alle playlist. Se elimini una playlist o un film, le righe qui dentro si cancellano da sole
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_film (
            playlist_id INTEGER NOT NULL,
            film_id INTEGER NOT NULL,
            data_aggiunta DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (playlist_id, film_id),
            FOREIGN KEY (playlist_id) REFERENCES playlist (id) ON DELETE CASCADE,
            FOREIGN KEY (film_id) REFERENCES film (id) ON DELETE CASCADE
        )
    """)
    
    # 5. Tabella Commenti
    # Sostituisce elementi_video. Ora tiene traccia di QUALE utente ha commentato QUALE film e QUANDO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id INTEGER NOT NULL,
            utente_id INTEGER NOT NULL,
            testo TEXT NOT NULL,
            data_commento DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (film_id) REFERENCES film (id) ON DELETE CASCADE,
            FOREIGN KEY (utente_id) REFERENCES utenti (id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()

    # Popolamento iniziale se la tabella film è vuota
    cursor.execute("SELECT COUNT(*) FROM film")
    if cursor.fetchone()[0] == 0:
        # Lista di 15 tuple (titolo, trama, anno, url_locandina, tmdb_id)
        film_esempi = [
            ("Inception", "Un ladro che ruba segreti aziendali attraverso l'uso della tecnologia di condivisione dei sogni riceve il compito inverso di piantare un'idea nella mente di un CEO.", 2010, "https://www.themoviedb.org/t/p/w600_and_h900_face/5QHWgqaBxZI1eM5e3YhyKzY5o3z.jpg", "27205"),
            ("The Matrix", "Un hacker scopre da misteriosi ribelli la vera natura della sua realtà e il suo ruolo nella guerra contro i suoi controllori.", 1999, "https://www.themoviedb.org/t/p/w600_and_h900_face/yQZX4scmfYtj4ccKFNGZJlOj1y9.jpg", "603"),
            ("Interstellar", "Un gruppo di esploratori viaggia attraverso un wormhole nello spazio nel tentativo di garantire la sopravvivenza dell'umanità.", 2014, "https://www.themoviedb.org/t/p/w600_and_h900_face/bMKiLh0mES4Uiococ240lbbTGXQ.jpg", "157336"),
            ("Il Gladiatore", "Un ex generale romano cerca vendetta contro l'imperatore corrotto che ha assassinato la sua famiglia e lo ha condannato alla schiavitù.", 2000, "https://www.themoviedb.org/t/p/w600_and_h900_face/euOKjQaV1QXtzLyNZAa1PMHGJlJ.jpg", "98"),
            ("Pulp Fiction", "Le vite di due assassini della mafia, di un pugile, della moglie di un gangster e di una coppia di banditi di periferia si intrecciano in quattro storie di violenza e redenzione.", 1994, "https://www.themoviedb.org/t/p/w600_and_h900_face/hOpN58hkQGZph5LHhyRrryy1hzF.jpg", "680"),
            ("Fight Club", "Un impiegato insonne e un disinvolto produttore di sapone formano un club di combattimento clandestino che si evolve in qualcosa di molto più grande.", 1999, "https://www.themoviedb.org/t/p/w600_and_h900_face/rtNLQ8HbPElzEfrHjrzSr07prKT.jpg", "550"),
            ("Il Cavaliere Oscuro", "Quando la minaccia nota come il Joker semina caos e distruzione a Gotham City, Batman deve accettare uno dei più grandi test psicologici e fisici della sua vita.", 2008, "https://www.themoviedb.org/t/p/w600_and_h900_face/qIhsgno1mjbzUbs4H6DaRjhskAR.jpg", "155"),
            ("Forrest Gump", "Le presidenze di Kennedy e Johnson, gli eventi del Vietnam, del Watergate e altre vicende storiche si snodano attraverso la prospettiva di un uomo dell'Alabama con un basso quoziente intellettivo.", 1994, "https://www.themoviedb.org/t/p/w600_and_h900_face/gsbmOBQKIzO3q57pITk9Ol4urV2.jpg", "13"),
            ("Avatar", "Un marine paraplegico inviato sul pianeta Pandora in una missione unica si ritrova diviso tra il seguire gli ordini e il proteggere il mondo che sente come la sua nuova casa.", 2009, "https://www.themoviedb.org/t/p/w600_and_h900_face/cu6CTvQqVvaTUmWNGWydpf7EzmV.jpg", "19995"),
            ("La Città Incantata", "Durante il trasloco della sua famiglia in periferia, una bambina di 10 anni vaga in un mondo governato da dei, streghe e spiriti, dove gli umani vengono trasformati in bestie.", 2001, "https://www.themoviedb.org/t/p/w600_and_h900_face/3PV6lq9BNmoyyDXr5tdNeeESEMn.jpg", "129"),
            ("Spider-Man: Into the Spider-Verse", "Il adolescente Miles Morales diventa lo Spider-Man del suo universo e deve unirsi ad altri cinque eroi ragno provenienti da altre dimensioni per fermare una minaccia totale.", 2018, "https://www.themoviedb.org/t/p/w600_and_h900_face/7pgJHduD3OVwF3EGFnGBq0nOUYv.jpg", "324857"),
            ("Whiplash", "Un promettente giovane batterista si iscrive a un conservatorio musicale d'élite dove i suoi sogni di grandezza sono guidati da un istruttore che non si fermerà davanti a nulla pur di realizzare il potenziale dello studente.", 2014, "https://www.themoviedb.org/t/p/w600_and_h900_face/jQwkXN38AGrK2s3LJqxZow1Ic7z.jpg", "244786"),
            ("Parasite", "L'avidità e la discriminazione di classe minacciano il neonato rapporto simbiotico tra la ricca famiglia Park e la famiglia Kim, decisamente meno abbiente.", 2019, "https://www.themoviedb.org/t/p/w600_and_h900_face/mMM8kcfspicib7AmPTvf97Rarwn.jpg", "496243"),
            ("Il Signore degli Anelli: La Compagnia dell'Anello", "Un timido Hobbit della Contea e otto compagni intraprendono un viaggio per distruggere il potente Unico Anello e salvare la Terra di Mezzo dal Signore Oscuro Sauron.", 2001, "https://www.themoviedb.org/t/p/w600_and_h900_face/iZTDPQYgr3rhL7hPIYFt17ATp8.jpg", "120"),
            ("Star Wars: Una Nuova Speranza", "Luke Skywalker unisce le forze con un cavaliere Jedi, un pilota arrogante, un Wookiee e due droidi per salvare la galassia dall'arma di distruzione di massa dell'Impero, salvando la principessa Leia.", 1977, "https://www.themoviedb.org/t/p/w600_and_h900_face/aWq0skBAaZYzZFVdiJwqF0bU4NO.jpg", "11")
        ]

        # Inseriamo i dati definendo solo le colonne della lista fornita.
        # La colonna "url_trailer" rimarrà temporaneamente NULL (vuota) per questi film, pronta per essere aggiornata in seguito.
        cursor.executemany("""
            INSERT INTO film (titolo, trama, anno, url_locandina, tmdb_id) 
            VALUES (?, ?, ?, ?, ?)
        """, film_esempi)

        conn.commit()
        print("Inseriti con successo 15 film di prova nel database!")
        
    conn.close()

if __name__ == "__main__":
    dbinit()