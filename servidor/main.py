import threading
from servidor.core.http_server import start_http_server
from servidor.core.udp_server import start_udp_server

if __name__ == "__main__":
    # Inicializa o Servidor HTTP (TCP)
    t_http = threading.Thread(target=start_http_server)
    t_http.daemon = True
    t_http.start()
    
    # Inicializa o Servidor UDP Real
    t_udp = threading.Thread(target=start_udp_server)
    t_udp.daemon = True
    t_udp.start()
    
    print("[SISTEMA] Backend (HTTP/UDP) rodando em paralelo.")
    t_http.join()