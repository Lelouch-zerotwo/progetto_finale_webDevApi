//const API_URL = "https://bookish-goggles-5vgg74gxjgww2r5w-8000.app.github.dev";
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

// 1. Legge le playlist dal Back-end 
async function caricaPlaylist() {
    let res = await fetch(`${API_URL}/playlist?token=${token}`); 
    let liste = await res.json(); 
    let ul = document.getElementById("listaPlaylist");
    ul.innerHTML = liste.length === 0 ? "<p>Non hai ancora creato nessuna playlist.</p>" : "";

    liste.forEach(l => {
        let li = document.createElement("li");
        li.textContent = l.titolo_playlist;
        li.onclick = () => mostraDettaglio(l.titolo_playlist);
        ul.appendChild(li);
    });
}

// 2. Crea una nuova playlist 
async function creaNuovaPlaylist() {
    let titolo = document.getElementById("nomePlaylist").value.trim();
    if(!titolo) return;

    let res = await fetch(`${API_URL}/playlist?token=${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ titolo_playlist: titolo })
    });

    if(res.ok) {
        alert("Playlist registrata!");
        document.getElementById("nomePlaylist").value = "";
        caricaPlaylist();
    }
}

// 3. Mostra i film associati tramite JOIN alla playlist cliccata 
async function mostraDettaglio(titolo) {
    playlistSelezionata = titolo;
    document.getElementById("titoloPlaylistAttiva").textContent = "Dettaglio: " + titolo;
            
    let res = await fetch(`${API_URL}/playlist/dettaglio?titolo=${encodeURIComponent(titolo)}&token=${token}`);
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

// 4. Popola il menu a tendina (select) prendendo tutti i film esistenti
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

// 5. Salva la relazione film-playlist 
async function aggiungiFilmAPlaylist() {
    let idFilm = document.getElementById("selectFilm").value;
    if(!idFilm || !playlistSelezionata) 
        return;

    let res = await fetch(`${API_URL}/playlist/aggiungi-film?titolo_p=${encodeURIComponent(playlistSelezionata)}&id_f=${idFilm}&token=${token}`, {method: "POST"});

    if(res.ok) {
        alert("Film abbinato!");
        mostraDettaglio(playlistSelezionata);
    }
}