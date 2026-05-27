const API_URL = 'http://127.0.0.1:5000';
let currentUser = null;
let pollingInterval = null;
let ultimoEnvioDigitando = 0;

async function autenticar(rota) {
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value.trim();

    if (!user || !pass) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${rota}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            if (rota === 'login') {
                currentUser = user;
                document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('chat-screen').style.display = 'block';
                const chatScreen = document.getElementById("chat-screen");
                chatScreen.style.display = "flex"; 
                document.getElementById("main-box").classList.add("chat-fullscreen");
                document.getElementById('welcome-msg').innerText = `Ligado como: ${currentUser}`;
                
                carregarMensagens();
                pollingInterval = setInterval(carregarMensagens, 1000);
            } else {
                alert('Conta criada com sucesso! Faça login.');
            }
        } else {
            alert(data.message || 'Ocorreu um erro na operação.');
        }
    } catch (error) {
        alert('Erro ao conectar ao servidor HTTP backend.');
    }
}


async function notificarDigitando() {
    const agora = Date.now();
    if (agora - ultimoEnvioDigitando < 2000) return; 
    ultimoEnvioDigitando = agora;

    try {
        await fetch(`${API_URL}/typing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser })
        });
    } catch (e) {
        console.error(e);
    }
}

async function enviarMensagem() {
    const input = document.getElementById('msg-input');
    const content = input.value.trim();
    if (!content) return;

    try {
        const response = await fetch(`${API_URL}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, content: content })
        });

        if (response.ok) {
            input.value = '';
            carregarMensagens();
        } else {
            const data = await response.json();
            alert(data.message || 'Erro ao enviar.');
        }
    } catch (error) {
        alert('Erro de rede ao tentar enviar a mensagem.');
    }
}

async function carregarMensagens() {
    try {
        const response = await fetch(`${API_URL}/messages`);
        if (!response.ok) return;
        
        const dados = await response.json();
        const mensagens = dados.mensagens || [];
        const quemEstaDigitando = dados.digitando || "";
        
        const box = document.getElementById('chat-box');
        const statusDiv = document.getElementById('typing-status');
        
        const estavaNoFundo = box.scrollHeight - box.clientHeight <= box.scrollTop + 50;

        box.innerHTML = '';
        mensagens.forEach(m => {
            box.innerHTML += `<div class="msg"><strong>${m.sender}:</strong> ${m.content}</div>`;
        });

        if (estavaNoFundo) {
            box.scrollTop = box.scrollHeight;
        }

        if (quemEstaDigitando && quemEstaDigitando !== currentUser) {
            statusDiv.innerText = `${quemEstaDigitando} está a digitar...`;
        } else {
            statusDiv.innerText = '';
        }
    } catch (error) {
        console.error('Erro no polling:', error);
    }
}

function desconectar() {
    document.getElementById("chat-screen").style.display = "none";
    document.getElementById("auth-screen").style.display = "block";
    document.getElementById("main-box").classList.remove("chat-fullscreen");
    document.getElementById("password").value = "";
    document.getElementById("msg-input").value = "";
    document.getElementById("chat-box").innerHTML = "";

}