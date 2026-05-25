````md


## Descrição Geral

Este projeto é um sistema de chat híbrido multiusuário desenvolvido em Python para a disciplina de Redes de Computadores da Universidade de Brasília (UnB). O projeto integra comunicação HTTP/TCP e UDP com persistência em SQLite e interface Web em HTML/JavaScript.

O objetivo principal é demonstrar conceitos das camadas de Aplicação e Transporte do modelo Internet, permitindo análise prática de protocolos, desempenho de rede e captura de tráfego utilizando Wireshark.

---

# Arquitetura do Sistema

O sistema é dividido em três componentes principais:

## Backend

Servidor desenvolvido em Python 3 utilizando apenas bibliotecas nativas:

- `http.server`
- `socket`
- `threading`
- `sqlite3`

Responsável por:

- Cadastro de usuários
- Login
- Envio e recuperação de mensagens
- Logs e auditoria
- Comunicação HTTP e UDP

## Banco de Dados

Persistência utilizando SQLite para armazenamento de:

- Usuários
- Mensagens
- Logs de sistema
- Eventos de segurança

Regras implementadas:

- Chaves estrangeiras (`FOREIGN KEY`)
- Restrição de unicidade (`UNIQUE`)
- Exclusão em cascata (`ON DELETE CASCADE`)

## Frontend

Cliente Web executado diretamente no navegador utilizando:

- HTML5
- CSS3
- JavaScript puro
- Requisições assíncronas via `fetch`

---

# Comunicação HTTP/TCP

O servidor HTTP opera na porta `5000` seguindo o protocolo HTTP/1.1.

## Endpoints

### Cadastro

```http
POST /register
```

### Login

```http
POST /login
```

### Envio de mensagens

```http
POST /messages
```

### Histórico de mensagens

```http
GET /messages
```

---

# Framing e Controle de Payload

Como o TCP trabalha com fluxo contínuo de bytes, o servidor utiliza o cabeçalho `Content-Length` para leitura correta dos dados recebidos.

Exemplo:

```python
self.rfile.read(content_length)
```

O backend também implementa limitação de mensagens em até 500 caracteres para evitar abuso de memória e ataques simples de negação de serviço.

```python
if len(content) > 500:
```

Caso o limite seja excedido:

- A requisição é bloqueada
- O servidor retorna HTTP 400
- Um evento `ALERTA_SEGURANCA` é registrado

---

# Comunicação UDP

O servidor UDP opera paralelamente na porta `5001` utilizando:

```python
socket.SOCK_DGRAM
```

Características:

- Sem conexão
- Sem handshake
- Sem ACK
- Baixa latência

O objetivo é permitir comparação prática entre TCP e UDP em ferramentas como Wireshark.

---

# CORS

Para permitir acesso do frontend local ao backend, o servidor implementa suporte a CORS:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

# Execução

## Inicialização do Backend

```bash
python3 -m servidor.main
```

## Inicialização do Frontend

Abrir diretamente no navegador:

```plaintext
cliente_desktop/index.html
```

---

# Portas Utilizadas

| Protocolo | Porta | Função |
|---|---|---|
| TCP | 5000 | API HTTP |
| UDP | 5001 | Tráfego Analítico |

---

# Testes Realizados

- Login inválido (`401 Unauthorized`)
- Cadastro duplicado (`400 Bad Request`)
- Bloqueio de payload acima de 500 bytes
- Registro de eventos de segurança
- Captura e análise de tráfego TCP e UDP no Wireshark

---

# Considerações Finais

O SocketSync foi desenvolvido para consolidar conhecimentos práticos sobre:

- Protocolo HTTP
- Transporte TCP e UDP
- Manipulação manual de sockets
- Persistência relacional
- Integridade de dados
- Controle de payload
- Auditoria de eventos
- Métricas de rede

A coexistência de TCP e UDP no mesmo ambiente permite análises comparativas de desempenho, overhead e confiabilidade entre protocolos de transporte.
````

