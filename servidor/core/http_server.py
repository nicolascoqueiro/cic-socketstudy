from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import time
from servidor.database.db_manager import DBManager
from servidor.core.udp_server import estado_compartilhado

db = DBManager()

class CustomHTTPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode('utf-8'))

        if self.path == '/register':
            user = data.get("username", "")
            senha = data.get("password", "")
            if db.register_user(user, senha):
                db.log_event("HTTP_REGISTER", f"Usuário {user} cadastrado.")
                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "success", "message": "Cadastrado com sucesso"}).encode())
            else:
                self.send_error(400, "Utilizador ja existe")

        elif self.path == '/login':
            user = data.get("username", "")
            senha = data.get("password", "")
            if db.authenticate_user(user, senha):
                db.log_event("HTTP_LOGIN", f"Usuário {user} autenticado.")
                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "success", "message": "Autenticado com sucesso"}).encode())
            else:
                self.send_error(401, "Credenciais incorretas")

        # NOVA ROTA: Transforma o clique do teclado em um Pacote UDP Real
        elif self.path == '/typing':
            user = data.get("username", "")
            
            # Cria um socket UDP rápido e injeta o evento na porta 5001
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = {"username": user, "status": "digitando"}
            sock.sendto(json.dumps(payload).encode('utf-8'), ("127.0.0.1", 5001))
            sock.close()
            
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "success"}).encode())

        elif self.path == '/messages':
            user = data.get("username", "")
            content = data.get("content", "")
            if len(content) > 500:
                db.log_event("ALERTA_SEGURANCA", f"Mensagem com tamanho {len(content)} rejeitada.")
                self.send_error(400, "Mensagem excede o limite de 500 caracteres.")
                return

            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM usuarios WHERE username = ?", (user,))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                    cursor.execute("INSERT INTO mensagens (sender_id, content) VALUES (?, ?)", (user_id, content))
                    conn.commit()
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"status": "success"}).encode())
                else:
                    self.send_error(404, "Usuario nao encontrado")

    def do_GET(self):
        if self.path == '/messages':
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.username, m.content 
                    FROM mensagens m 
                    JOIN usuarios u ON m.sender_id = u.id 
                    ORDER BY m.id ASC
                """)
                mensagens = [{"sender": row[0], "content": row[1]} for row in cursor.fetchall()]
            
            quem_digita = ""
            if time.time() - estado_compartilhado["timestamp"] < 3:
                quem_digita = estado_compartilhado["username"]

            resposta = {"mensagens": mensagens, "digitando": quem_digita}
            self._set_headers(200)
            self.wfile.write(json.dumps(resposta).encode())

def start_http_server():
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, CustomHTTPHandler)
    print("[HTTP SERVER] Escutando nativamente na porta 5000...")
    httpd.serve_forever()