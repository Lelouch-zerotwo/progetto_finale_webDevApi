//ricordarsi di mettere la porta 8000 pubblica
        
//const API_URL = "https://bookish-goggles-5vgg74gxjgww2r5w-8000.app.github.dev";
const API_URL = "";

function controllaStato() {
    const token = localStorage.getItem("session_token");
    const box = document.getElementById("statoSessione");
    if(token) {
        box.style.color = "#16a34a";
        box.textContent = "Sessione attiva. Sei loggato!";
    } else {
        box.style.color = "#dc2626";
        box.textContent = "Nessun utente connesso.";
    }
}

async function eseguiRegistrazione() {
    let user = document.getElementById("regUser").value.trim();
    let pass = document.getElementById("regPass").value.trim();
    if(!user || !pass){
        alert("Compila tutti i campi!"); 
        return; 
    }

    let risposta = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass })
    });

    let dati = await risposta.json();
    if(risposta.ok) {
        alert("Registrazione completata!");
        document.getElementById("regUser").value = "";
        document.getElementById("regPass").value = "";
    } else 
        alert("Errore: " + dati.detail); 
}

async function eseguiLogin() {
    let user = document.getElementById("logUser").value.trim();
    let pass = document.getElementById("logPass").value.trim();
    if(!user || !pass){
        alert("Inserisci le credenziali!"); 
        return; 
    }

    let risposta = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass })
    });

    let dati = await risposta.json();
    if(risposta.ok) {
        localStorage.setItem("session_token", dati.token);
        alert("Accesso autorizzato!");
        document.getElementById("logUser").value = "";
        document.getElementById("logPass").value = "";
        controllaStato();
    } else 
        alert("Accesso negato: " + dati.detail); 
    }

function eseguiLogout() {
    localStorage.removeItem("session_token");
    alert("Logout effettuato.");
    controllaStato();
}

window.onload = controllaStato;