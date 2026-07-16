const API_URL = "";
const token = localStorage.getItem("session_token"); 

if(token) {
    document.getElementById("boxInserimentoFilm").style.display = "block";
    document.getElementById("formRecensione").style.display = "block";
}

async function avviaRicerca() {
    let ricerca = document.getElementById("campoCerca").value.trim();
    let contenitore = document.getElementById("risultati");
            
    contenitore.innerHTML = "<p>Caricamento in corso...</p>";
    let url = ricerca === "" ? `${API_URL}/film` : `${API_URL}/film/cerca?keyword=${encodeURIComponent(ricerca)}`; 
            
    try {
        let reply = await fetch(url);
                
        if (!reply.ok) 
            throw new Error(`Errore dal server: ${reply.status}`);
        
        let film = await reply.json();
        contenitore.innerHTML = ""; 

        if (!film || film.length === 0) {
            contenitore.innerHTML = "<p>Nessun film trovato nel database locale.</p>";
            return;
        }

        for (let f of film) { 
            let div = document.createElement("div");
            div.className = "card-film"; 
                    
            let img = document.createElement("img");
            img.src = f.url_locandina || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=400";
                    
            let titolo = document.createElement("h3");
            titolo.textContent = f.titolo; 
                    
            let anno = document.createElement("p");
            anno.textContent = "Anno: " + f.anno;

            let btn = document.createElement("button");
            btn.textContent = "Apri Scheda";
            btn.onclick = () => apriScheda(f.id); 
                    
            div.appendChild(img);
            div.appendChild(titolo);
            div.appendChild(anno);
            div.appendChild(btn);
                    
            contenitore.appendChild(div);  
        }
    } catch (error) {
        contenitore.innerHTML = `
            <div style="color: #dc2626; background: #fee2e2; padding: 15px; border-radius: 6px;">
                <p><b>Impossibile connettersi al database.</b></p>
            </div>
        `;
    }
}

async function apriScheda(idFilm) {
    try {
        let reply = await fetch(`${API_URL}/film/${idFilm}`); 
        
        if(reply.ok) {
            let dati = await reply.json();
            let f = dati.film;
            let commenti = dati.commenti;

            document.getElementById("schedaTitolo").textContent = f.titolo;
            document.getElementById("schedaAnno").textContent = f.anno;
            document.getElementById("schedaTrama").textContent = f.trama; 
            document.getElementById("schedaImmagine").src = f.url_locandina;
            document.getElementById("recFilmId").value = f.id;

            let boxCommenti = document.getElementById("listaCommenti");
            boxCommenti.innerHTML = commenti.length === 0 ? "<p>Non ci sono recensioni per ora. Sii il primo!</p>" : "";
                    
            commenti.forEach(c => {
                let d = document.createElement("div");
                d.className = "commento-item";
                let dataFormattata = new Date(c.data_commento + "Z").toLocaleDateString("it-IT");
                
                let spanUtente = document.createElement("span");
                spanUtente.innerHTML = `👤 <b>${c.username}</b> <i>(${dataFormattata})</i>: <br> 💬 `;
                
                let spanTesto = document.createElement("span");
                spanTesto.textContent = c.testo;
                
                d.appendChild(spanUtente);
                d.appendChild(spanTesto);
                boxCommenti.appendChild(d);
            });

            document.getElementById("schedaFilm").style.display = "block"; 
            document.getElementById("schedaFilm").scrollIntoView({ behavior: "smooth"});
            
        } else {
            // SE IL SERVER VA IN ERRORE (es. 500 o 404)
            alert(`Ops! Il server ha restituito un errore ${reply.status}. Controlla il terminale di VS Code per i dettagli!`);
        }
        
    } catch (error) {
        // SE C'È UN ERRORE DI RETE O JAVASCRIPT CRASHA
        console.error("Errore di esecuzione:", error);
        alert("Errore di comunicazione col server. Apri la console del browser (F12) per leggere l'errore tecnico.");
    }
}

async function inserisciFilmManuale() {
    let titolo = document.getElementById("newTitolo").value.trim();
    let trama = document.getElementById("newTrama").value.trim();
    let anno = document.getElementById("newAnno").value;
    let url_locandina = document.getElementById("newPoster").value.trim();
    let tmdb_id = document.getElementById("newTmdb").value.trim();
    let url_trailer = document.getElementById("newTrailer").value.trim();

    if(!titolo || !trama) { 
        alert("Inserisci titolo e trama!"); 
        return; 
    }

    let reply = await fetch(`${API_URL}/film`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}` 
        },
        body: JSON.stringify({ 
            titolo: titolo, 
            trama: trama, 
            anno: parseInt(anno), 
            url_locandina: url_locandina, 
            url_trailer: url_trailer || null,
            tmdb_id: tmdb_id 
        })
    });

    if(reply.ok) {
        alert("Film inserito correttamente!");
        location.reload();
    } else { 
        alert("Errore di caricamento. Verifica di aver effettuato il login."); 
    }
}

async function inviaCommento() {
    let idFilm = document.getElementById("recFilmId").value;
    let commento = document.getElementById("recTesto").value.trim();

    if(!commento) { 
        alert("Inserisci il testo della recensione!"); 
        return; 
    }

    let reply = await fetch(`${API_URL}/film/${idFilm}/commento`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ testo: commento })
    });

    if(reply.ok) {
        alert("Recensione inserita!");
        apriScheda(idFilm);
        document.getElementById("recTesto").value = "";
    } else {
        alert("Sessione scaduta o non valida.");
    }
}

window.onload = avviaRicerca;