# cic-socketstudy

Projeto prático desenvolvido para a disciplina **CIC0124 - Redes de Computadores** na Universidade de Brasília (UnB).

## Integrantes
* **Nicolas Coqueiro Almeida de Freitas** 
* **Maria  **
**Professora:** Profa. Priscila Solis 

---

## Sobre o Projeto
O projeto consiste em um **Sistema de Chat Híbrido Multiusuário** baseado na arquitetura Web, implementando os conceitos fundamentais das camadas de Aplicação e Transporte. A plataforma integra requisições tradicionais sobre o protocolo HTTP com disparos rápidos via sockets não-orientados à conexão (UDP), permitindo a análise comparativa de desempenho exigida no escopo acadêmico.

### Tecnologias Utilizadas
* **Servidor Central (Backend):** Python 3 (`http.server` nativo, Sockets e Threading)
* **Banco de Dados:** SQLite (Controle de unicidade, chaves estrangeiras com cascateamento e logs históricos)
* **Interface do Usuário (Frontend):** Cliente Web Nativo (HTML5, CSS3 e JavaScript assíncrono com Polling)
* **Análise de Protocolos:** Wireshark (Captura de pacotes, metrificação de RTT, Throughput e overhead de cabeçalhos)

---

## Objetivos Alcançados (Especificação da Disciplina)
1. **Protocolo HTTP Nativo:** Processamento de requisições `GET`, `POST` e pre-flight `OPTIONS` (CORS), sem dependência de frameworks externos.
2. **Defesa de Integridade de Dados:** Validação estrita de pacotes no backend com limitação rígida de carga útil para mensagens (máximo de 500 caracteres/bytes).
3. **Persistência Relacional Segura:** Banco de dados estruturado com tratamento nativo de chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`) e restrição de unicidade (`UNIQUE`) para credenciais.
4. **Cenário Comparativo (TCP x UDP):** Fluxo de mensagens estruturado via requisições HTTP (sobre TCP) concorrentes operando em paralelo a um motor UDP isolado projetado para testes de estresse e perda de datagramas.

---

## Modelagem Arquitetural (UML)

### Visão Geral do Fluxo (Diagrama de Classes)

O fluxo detalha a comunicação híbrida empregada no projeto: transações estruturadas de cadastro, login e mensagens utilizam canais síncronos HTTP/TCP, enquanto fluxos independentes operam via UDP para fins de amostragem de tráfego.

![Diagrama de Classes](docs/uml.png)

---

## Arquitetura do Projeto

```text
├── .gitignore
├── README.md                    # Descrição, integrantes e especificações do projeto
├── docs/                        # Documentação técnica e relatórios

(em construção)
│   ├── protocolo_aplicacao.md  # Especificação dos métodos HTTP e JSONs aceitos
│   ├── relatorio_wireshark.pdf # Análises de atraso, vazão e capturas de tráfego
│   └── uml_classes.png         # Imagem do Diagrama de Classes
│
├── servidor/                    
│   ├── main.py                  # Inicializador unificado do backend (HTTP e UDP)
│   ├── core/                    # Motores de rede
│   │   ├── __init__.py
│   │   ├── http_server.py       # Servidor HTTP nativo (GET/POST) com limite de 500 bytes
│   │   └── udp_server.py        # Servidor para testes de tráfego rápido em background
│   ├── database/                # Camada de persistência relacional
│   │   ├── __init__.py
│   │   ├── chat_database.db     # Banco SQLite local (ignorado no versionamento)
│   │   └── db_manager.py        # Gerenciador de queries, constraints e logs
│   └── logs/
│        └── server.log
├── cliente_desktop/                    
│   ├── app.js                 
│   ├── index.html
│    └── style.css
│
└── cliente_desktop/             
    ├── index.html               # Frontend Web - Tela de Autenticação e Janela do Chat
    └── network/                 # Scripts auxiliares para medição de RTT e Throughput
