//const API_URL = "https://bookish-goggles-5vgg74gxjgww2r5w-8000.app.github.dev";
const API_URL = "";
const token = localStorage.getItem("session_token"); 

// Mostra i form di inserimento dati solo se l'utente ha effettuato il login
if(token) {
    document.getElementById("boxInserimentoFilm").style.display = "block";
    document.getElementById("formRecensione").style.display = "block";
}

        
async function avviaRicerca() {
    let ricerca = document.getElementById("campoCerca").value.trim();
    let contenitore = document.getElementById("risultati");
            
    // Mostra un feedback all'utente mentre carica
    contenitore.innerHTML = "<p>Caricamento in corso...</p>";

    let url = ricerca === "" ? `${API_URL}/film` : `${API_URL}/film/cerca?keyword=${encodeURIComponent(ricerca)}`; 
            
    try {
        let reply = await fetch(url);
                
        // Se il server risponde con un errore (es. 404 o 500)
        if (!reply.ok) 
            throw new Error(`Errore dal server: ${reply.status}`);
        

        let film = await reply.json();
        console.log("Dati ricevuti:", film);
                
        contenitore.innerHTML = ""; // Svuota il messaggio di caricamento

        if (!film || film.length === 0) {
            contenitore.innerHTML = "<p>Nessun film trovato nel database locale.</p>";
            return;
        }

        // Utilizziamo il ciclo completo (quello che prima era commentato)
        for (let f of film) { 
            let div = document.createElement("div");
            // Applica la classe per la griglia e lo stile grafico
            div.className = "card-film"; 
                    
            let img = document.createElement("img");
            // Se non c'è una locandina, mette un'immagine segnaposto
            img.src = f.url_locandina || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=400";
                    
            let titolo = document.createElement("h3");
            titolo.textContent = f.titolo; 
                    
            let anno = document.createElement("p");
            anno.textContent = "Anno: " + f.anno;

            let btn = document.createElement("button");
            btn.textContent = "Apri Scheda";
            // Collega il click alla funzione apriScheda passando l'ID del film
            btn.onclick = () => apriScheda(f.id); 
                    
            div.appendChild(img);
            div.appendChild(titolo);
            div.appendChild(anno);
            div.appendChild(btn);
                    
            contenitore.appendChild(div);  
        }
    } catch (error) {
        console.error("Fetch fallito:", error);
        contenitore.innerHTML = `
            <div style="color: #dc2626; background: #fee2e2; padding: 15px; border-radius: 6px;">
                <p><b>Impossibile connettersi al database.</b></p>
                <p>Verifica che il tuo GitHub Codespace sia in esecuzione e che la porta 5500 sia impostata su <b>"Public"</b> anziché "Private".</p>
            </div>
        `;
    }
}

async function apriScheda(idFilm) {
    let reply = await fetch(`${API_URL}/film/${idFilm}`); 
    if(reply.ok){
        let dati = await reply.json();
        let f = dati.film;
        let commenti = dati.commenti;

        document.getElementById("schedaTitolo").textContent = f.titolo;
        document.getElementById("schedaAnno").textContent = f.anno;
        document.getElementById("schedaTrama").textContent = f.trama; 
        document.getElementById("schedaImmagine").src = f.url_locandina;
        document.getElementById("recFilmId").value = f.id;

        let boxCommenti = document.getElementById("listaCommenti");
        boxCommenti.innerHTML = commenti.length === 0 ? "<p>Non ci sono video abbinati per ora.</p>" : "";
                
        commenti.forEach(c => {
            let d = document.createElement("div");
            d.className = "commento-item";
            d.innerHTML = `🎥 <b>Video:</b> <a href="${c.url_video_youtube}" target="_blank">${c.url_video_youtube}</a> <br> 💬 <b>Nota:</b> ${c.commento}`;
            boxCommenti.appendChild(d);
        });

        document.getElementById("schedaFilm").style.display = "block"; 
        document.getElementById("schedaFilm").scrollIntoView({ behavior: "smooth"});
    }
}

async function inserisciFilmManuale() {
    let titolo = document.getElementById("newTitolo").value.trim();
    let trama = document.getElementById("newTrama").value.trim();
    let anno = document.getElementById("newAnno").value;
    let url_locandina = document.getElementById("newPoster").value.trim();
    let tmdb_id = document.getElementById("newTmdb").value.trim();

    if(!titolo || !trama) { 
        alert("Inserisci titolo e trama!"); 
        return; 
    }

    let reply = await fetch(`${API_URL}/film?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ titolo, trama, anno: parseInt(anno), url_locandina, tmdb_id })
    });

    if(reply.ok) {
        alert("Film inserito correttamente!");
        location.reload();
    } else { alert("Errore di caricamento."); }
}

async function inviaCommentoVideo() {
    let idFilm = document.getElementById("recFilmId").value;
    let urlVideo = document.getElementById("recUrl").value.trim();
    let commento = document.getElementById("recTesto").value.trim();

     if(!urlVideo || !commento) { alert("Completa i campi recensione!"); return; }

        let reply = await fetch(`${API_URL}/film/${idFilm}/commento?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url_video_youtube: urlVideo, commento: commento })
    });

    if(reply.ok) {
        alert("Recensione inserita!");
        apriScheda(idFilm);
        document.getElementById("recUrl").value = "";
        document.getElementById("recTesto").value = "";
    }
}

window.onload = avviaRicerca;