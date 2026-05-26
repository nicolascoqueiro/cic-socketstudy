# Especificação do Protocolo de Aplicação
**Disciplina:** Redes de Computadores 
**Contexto Acadêmico:** Ciência da computação – Universidade de Brasília (UnB) 

---

## 1. Visão Geral do Protocolo

O cic-socketstudy é um protocolo híbrido de camada de aplicação projetado para fornecer um ambiente de chat persistente, seguro e responsivo. A arquitetura de comunicação baseia-se no modelo Cliente-Servidor e utiliza duas estratégias de transporte de forma multiplexada para otimizar o desempenho:

1.  **Canal Confiável de Controle (HTTP sobre TCP - Porta 5000):** Gerencia ações estruturadas e persistentes que exigem garantia absoluta de entrega, ordenamento e tratamento de erros (Registro, Autenticação e Sincronização de Mensagens).
2.  **Canal de Alta Frequência (UDP Nativo - Porta 5001):** Gerencia sinalizações efêmeras e de alta volatilidade, onde a latência mínima é prioritária e perdas ocasionais de pacotes são toleradas pelo sistema (Estado de digitação do teclado: "*Digitando...*").

Todos os payloads trafegados na camada de aplicação utilizam codificação textual estruturada no formato **JSON (JavaScript Object Notation)** com codificação de caracteres **UTF-8**.
s
---

## 2. Canal de Controle e Persistência (HTTP/TCP)

O servidor HTTP escuta nativamente na porta `5000`. Todas as requisições enviadas pelo cliente devem conter o cabeçalho `Content-Type: application/json`. O servidor implementa políticas de segurança CORS (`Access-Control-Allow-Origin: *`) para permitir a comunicação multiplataforma.

### 2.1. Registro de Novo Usuário
Permite o cadastro de uma nova credencial única no banco de dados relacional.

* **Rota:** `/register`
* **Método HTTP:** `POST`
* **Payload do Cliente (JSON):**
    ```json
    {
      "username": "nicolas",
      "password": "senha_secreta_123"
    }
    ```
* **Respostas do Servidor:**
    * **`200 OK` (Sucesso):** Usuário cadastrado e registrado na tabela de auditoria.
        ```json
        {
          "status": "success",
          "message": "Cadastrado com sucesso"
        }
        ```
    * **`400 Bad Request` (Conflito):** O nome de usuário já existe no banco de dados (Violação da constraint `UNIQUE`).
        ```json
        {
          "status": "error",
          "message": "Utilizador ja existe"
        }
        ```

### 2.2. Autenticação de Usuário (Login)
Valida as credenciais fornecidas contra os hashes criptográficos/dados armazenados.

* **Rota:** `/login`
* **Método HTTP:** `POST`
* **Payload do Cliente (JSON):**
    ```json
    {
      "username": "nicolas",
      "password": "senha_secreta_123"
    }
    ```
* **Respostas do Servidor:**
    * **`200 OK` (Sucesso):** Credenciais válidas. Sessão liberada no cliente.
        ```json
        {
          "status": "success",
          "message": "Autenticado com sucesso"
        }
        ```
    * **`401 Unauthorized` (Falha):** Nome de usuário inexistente ou senha incorreta.
        ```json
        {
          "status": "error",
          "message": "Credenciais incorretas"
        }
        ```

### 2.3. Envio de Mensagem Textual
Envia um novo segmento de texto para o histórico global do chat. O corpo da mensagem possui uma restrição de segurança estrita na camada de aplicação: **máximo de 500 bytes**.

* **Rota:** `/messages`
* **Método HTTP:** `POST`
* **Payload do Cliente (JSON):**
    ```json
    {
      "username": "nicolas",
      "content": "Olá, esta é uma mensagem de teste para o projeto de redes."
    }
    ```
* **Respostas do Servidor:**
    * **`200 OK` (Sucesso):** Mensagem validada, vinculada ao `user_id` via chave estrangeira (`FOREIGN KEY`) e persistida com sucesso.
        ```json
        {
          "status": "success"
        }
        ```
    * **`400 Bad Request` (Excesso de Dados):** O tamanho do campo `content` violou o limite de segurança de 500 bytes. O evento é catalogado na tabela de logs de auditoria como `ALERTA_SEGURANCA`.
        ```json
        {
          "status": "error",
          "message": "Mensagem excede o limite de 500 caracteres."
        }
        ```
    * **`404 Not Found` (Inconsistência):** O usuário emissor não consta na base de dados.
        ```json
        {
          "status": "error",
          "message": "Usuario nao encontrado"
        }
        ```

### 2.4. Sincronização do Histórico e Estado (Polling)
Requisição periódica executada assintoticamente pelo cliente (intervalo de 1 segundo) para recuperar o histórico completo de mensagens ordenadas de forma ascendente e capturar o estado atual do canal UDP.

* **Rota:** `/messages`
* **Método HTTP:** `GET`
* **Payload do Cliente:** Vazio.
* **Resposta do Servidor (`200 OK`):** Retorna um objeto composto contendo o array completo de mensagens agregadas ao nome dos remetentes e o campo dinâmico `digitando`, que expõe quem está transmitindo datagramas UDP nos últimos 3 segundos.
    ```json
    {
      "mensagens": [
        {
          "sender": "nicolas1",
          "content": "Fala Nicolas, tudo certo?"
        },
        {
          "sender": "nicolas",
          "content": "Tudo funcionando por aqui, acabei de testar o banco!"
        }
      ],
      "digitando": "nicolas1"
    }
    ```
    *Nota: Se ninguém estiver digitando na rede ou o timestamp do último pacote UDP ultrapassar 3 segundos, o campo `"digitando"` retornará uma string vazia (`""`).*

### 2.5. Gatilho de Interface para Disparo UDP
Como os navegadores Web possuem restrições de segurança de caixa de areia (*sandbox*) que impedem a abertura de sockets UDP brutos a partir de scripts client-side, o cliente intercepta o evento de digitação na caixa de texto (`oninput`) e emite uma notificação rápida via HTTP para que o próprio núcleo do servidor simule e injete o pacote UDP localmente no loopback.

* **Rota:** `/typing`
* **Método HTTP:** `POST`
* **Payload do Cliente (JSON):**
    ```json
    {
      "username": "nicolas"
    }
    ```
* **Resposta do Servidor (`200 OK`):** O servidor gera um socket de transporte sem conexão e dispara um datagrama UDP para `127.0.0.1:5001`.
    ```json
    {
      "status": "success"
    }
    ```

---

## 3. Canal de Monitoramento em Tempo Real (UDP)

O motor assíncrono UDP escuta nativamente na porta `5001`. Este canal não possui handshakes, controle de congestionamento, buffers de ordenamento ou confirmações de recebimento (`ACK`). Os datagramas recebidos alteram diretamente e em tempo real as variáveis globais voláteis contidas na memória compartilhada do servidor central.

### 3.1. Datagrama de Sinalização de Estado do Teclado
Enviado continuamente em rajadas (*bursts*) a cada 200 milissegundos enquanto o usuário interage com o campo de inserção de texto.

* **Porta de Destino:** `5001`
* **Protocolo de Transporte:** `UDP`
* **Payload do Datagrama (JSON em texto puro):**
    ```json
    {
      "username": "nicolas",
      "status": "digitando"
    }
    ```

### 3.2. Regra de Ciclo de Vida do Estado (Timeout)
Ao receber o payload acima, o servidorUDP atualiza internamente a memória do sistema:
$$\text{Memória}[\text{"username"}] = \text{payload.username}$$
$$\text{Memória}[\text{"timestamp"}] = \text{Tempo Atual do Sistema (Epoch Time)}$$

A validade do estado na rede obedece à inequação:
$$\Delta t = t_{\text{atual}} - t_{\text{registro}} < 3\text{ segundos}$$

Caso o cliente pare de digitar, o script cessa o envio dos datagramas UDP. Ao estourar o limiar de $\Delta t \ge 3$, o servidor limpa o estado de forma automática, fazendo o aviso desaparecer da interface gráfica dos demais clientes conectados de maneira transparente.

---

## 4. Códigos de Erro e Auditoria do Sistema

O protocolo SocketSync mapeia eventos de falha e tentativas de violação diretamente na camada de persistência (`logs_sistema`), categorizando os seguintes tipos de log corporativo:

1.  **`HTTP_REGISTER`:** Registrado quando uma nova conta é criada com sucesso.
2.  **`HTTP_LOGIN`:** Registrado quando uma autenticação com sucesso é concluída.
3.  **`ALERTA_SEGURANCA`:** Disparado em tempo de execução quando o servidor intercepta requisições malformadas ou payloads que excedem o limite estrutural de 500 bytes na área de dados, aplicando o descarte imediato do segmento para proteção de transbordo de buffer (*buffer overflow*).
