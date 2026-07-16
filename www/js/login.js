const API_URL = "";

async function controllaStato() {
    const token = localStorage.getItem("session_token");
    const box = document.getElementById("statoSessione");
    
    if(!token) {
        box.style.color = "#dc2626";
        box.textContent = "Nessun utente connesso.";
        return;
    }

    try {
        let res = await fetch(`${API_URL}/profilo`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        
        if(res.ok) {
            let dati = await res.json();
            let dataScadenza = new Date(dati.scadenza + "Z"); 
            let dataFormattata = dataScadenza.toLocaleString("it-IT");

            box.style.color = "#16a34a";
            // Prevenzione XSS: lasciamo uno span vuoto per l'username
            box.innerHTML = `
                Sessione attiva. Benvenuto <b id="nomeUtenteSicuro"></b>!<br>
                <small style="color: #4b5563; margin-top:5px; display:block;">
                    ⏳ Il tuo accesso scadrà il: ${dataFormattata}
                </small>
            `;
            // Inseriamo l'username in modo sicuro come testo puro
            document.getElementById("nomeUtenteSicuro").textContent = dati.username;

        } else {
            localStorage.removeItem("session_token");
            box.style.color = "#dc2626";
            box.textContent = "La sessione è scaduta o non è valida. Effettua di nuovo il login.";
        }
    } catch(e) {
        box.style.color = "#d97706";
        box.textContent = "Impossibile verificare lo stato della sessione al momento.";
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
    } else {
        alert("Errore: " + dati.detail); 
    }
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
    } else {
        alert("Accesso negato: " + dati.detail); 
    }
}

function eseguiLogout() {
    localStorage.removeItem("session_token");
    alert("Logout effettuato.");
    controllaStato();
}

window.onload = controllaStato;