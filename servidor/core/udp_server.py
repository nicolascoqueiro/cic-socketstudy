import socket
import json
import time

# Dicionário global para compartilhar o estado com o servidor HTTP
estado_compartilhado = {"username": "", "timestamp": 0}

def start_udp_server():
    global estado_compartilhado
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5001

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"[UDP SERVER] Escutando nativamente na porta {UDP_PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            payload = json.loads(data.decode('utf-8'))
            
            # Se receber o status do script UDP, atualiza a memória compartilhada
            if payload.get("status") == "digitando":
                user = payload.get("username", "")
                estado_compartilhado["username"] = user
                estado_compartilhado["timestamp"] = time.time()
        except Exception as e:
            print(f"[UDP ERRO] {e}")