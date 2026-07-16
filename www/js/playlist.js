const API_URL = "";
const token = localStorage.getItem("session_token");
let playlistSelezionata = "";

if(!token) {            
    document.getElementById("areaBloccata").style.display = "block";
} else {            
    document.getElementById("areaContenuto").style.display = "block";            
    caricaPlaylist();            
    caricaSelettoreFilm();
}

async function caricaPlaylist() {
    let res = await fetch(`${API_URL}/playlist`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    }); 
    
    if(!res.ok) return;

    let liste = await res.json(); 
    let ul = document.getElementById("listaPlaylist");
    ul.innerHTML = liste.length === 0 ? "<p>Non hai ancora creato nessuna playlist.</p>" : "";

    liste.forEach(l => {
        let li = document.createElement("li");
        li.textContent = l.titolo; 
        li.onclick = () => mostraDettaglio(l.titolo); 
        ul.appendChild(li);
    });
}

async function creaNuovaPlaylist() {
    let titolo = document.getElementById("nomePlaylist").value.trim();
    if(!titolo) return;

    let res = await fetch(`${API_URL}/playlist`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ titolo: titolo })
    });

    if(res.ok) {
        alert("Playlist registrata!");
        document.getElementById("nomePlaylist").value = "";
        caricaPlaylist();
    } else {
        alert("Errore nella creazione della playlist.");
    }
}

async function mostraDettaglio(titolo) {
    playlistSelezionata = titolo;
    document.getElementById("titoloPlaylistAttiva").textContent = "Dettaglio: " + titolo;
            
    let res = await fetch(`${API_URL}/playlist/dettaglio?titolo=${encodeURIComponent(titolo)}`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });
    
    let film = await res.json();
            
    let grid = document.getElementById("gridFilmPlaylist");
    grid.innerHTML = film.length === 0 ? "<p style='grid-column: 1/-1;'>Questa playlist è vuota. Aggiungi dei film!</p>" : "";

    film.forEach(f => {
        let card = document.createElement("div");
        card.className = "mini-card";
        card.innerHTML = `<img src="${f.url_locandina}" style="width:100%; height:120px; object-fit:cover; border-radius:4px;"><br><b>${f.titolo}</b> (${f.anno})`;
        grid.appendChild(card);
    });

    document.getElementById("sezioneDettaglio").style.display = "block";
}

async function caricaSelettoreFilm() {
    let res = await fetch(`${API_URL}/film`);
    let film = await res.json();
    let select = document.getElementById("selectFilm");
    select.innerHTML = "";
    film.forEach(f => {
        let opt = document.createElement("option");
        opt.value = f.id;
        opt.textContent = f.titolo;
        select.appendChild(opt);
    });
}

async function aggiungiFilmAPlaylist() {
    let idFilm = document.getElementById("selectFilm").value;
    if(!idFilm || !playlistSelezionata) 
        return;

    let res = await fetch(`${API_URL}/playlist/aggiungi-film?titolo_p=${encodeURIComponent(playlistSelezionata)}&id_f=${idFilm}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
    });

    if(res.ok) {
        alert("Film abbinato!");
        mostraDettaglio(playlistSelezionata);
    }
}