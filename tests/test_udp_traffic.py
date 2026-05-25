import socket
import time
import json
import sys

def simular_digitando(username="nicolas", duracao_segundos=15):
    SERVER_IP = "127.0.0.1"
    UDP_PORT = 5001
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = {"username": username, "status": "digitando"}
    mensagem = json.dumps(payload).encode('utf-8')
    
    print(f"[UDP CLIENT] Enviando pacotes como: {username}")
    
    fim = time.time() + duracao_segundos
    contador = 0
    try:
        while time.time() < fim:
            sock.sendto(mensagem, (SERVER_IP, UDP_PORT))
            contador += 1
            time.sleep(0.2)
            sys.stdout.write(f"\rPacotes UDP enviados: {contador}")
            sys.stdout.flush()
    finally:
        sock.close()
        print("\n[UDP CLIENT] Concluído.")

if __name__ == "__main__":
    simular_digitando(username="nicolas", duracao_segundos=15)