# CriptoMonitor — API Python (POO + SQLite3 Relacional + Terminal & Web)

Aplicação desenvolvida em **Python** seguindo o paradigma de **Orientação a Objetos (POO)**, integrada ao banco de dados relacional **SQLite3** (4 tabelas relacionais com manutenção **CRUD** completa) e consumindo cotações em tempo real em **Reais (BRL)** da API pública da **Coinbase**.

O sistema conta com duas interfaces integradas ao mesmo banco de dados (`cripto.db`):
1. **Menu Interativo de Terminal (CMD):** interface em linha de comando com entrada/saída segura, tratamento de exceções e todas as operações CRUD nas 4 tabelas.
2. **Interface Web (Flask REST API + React/Vite):** painel visual com Termômetro de Cotação, Conversor Instantâneo e Carteira Virtual.

---

## Bibliotecas Instaladas (Python / Backend)

Listadas no arquivo [`backend/requirements.txt`](backend/requirements.txt):

| Biblioteca | Versão | Finalidade no Projeto |
| :--- | :--- | :--- |
| **`Flask`** | `3.1.3` | Criação do servidor backend e rotas REST (`/api/...`) |
| **`Flask-SQLAlchemy`** | `3.1.1` | ORM em Orientação a Objetos para mapear as 4 tabelas relacionais no **SQLite3** |
| **`requests`** | `2.34.2` | Consumo HTTP da API externa da Coinbase (`/v2/prices/{MOEDA}-BRL/spot`) |
| **`sqlite3`** | *(Nativa do Python)* | Motor de banco de dados relacional local (`instance/cripto.db`) |

*(No Frontend Web: `react`, `vite` e `lucide-react`, listadas em `frontend/package.json`.)*

---

## Arquitetura em Orientação a Objetos e Separação de Módulos

O código Python está organizado na pasta `backend/` com responsabilidades separadas por módulo:

```text
Projeto-API/
├── iniciar_terminal.bat      # Atalho para abrir o Menu Interativo no CMD (Terminal)
├── iniciar_projeto.bat       # Atalho para iniciar os servidores Backend + Frontend Web
├── backend/                  # Aplicação Python (POO + Flask + SQLite3)
│   ├── terminal.py           # Classe SistemaTerminalCripto (Menu de opções no CMD com CRUD)
│   ├── run.py                # Ponto de entrada do servidor da API Flask
│   ├── config.py             # Classe Config com o caminho do banco SQLite3
│   ├── requirements.txt      # Bibliotecas Python instaladas
│   └── app/
│       ├── __init__.py       # Inicialização do Flask, SQLAlchemy e criação das 4 tabelas
│       ├── models.py         # 4 Classes POO mapeadas para as 4 tabelas relacionais do SQLite3
│       ├── services.py       # Regras de negócio, integração Coinbase e funções CRUD
│       └── routes.py         # Endpoints HTTP (GET, POST, PUT, DELETE)
└── frontend/                 # Interface Web (React + Vite)
```

---

## Banco de Dados SQLite3 — 4 Tabelas Relacionais

Definidas em [`backend/app/models.py`](backend/app/models.py) utilizando classes Python (`db.Model`), chaves primárias (`primary_key=True`), chaves estrangeiras (`db.ForeignKey`) e relacionamentos (`db.relationship`):

1. **`moedas` (Classe `Moeda`):**
   - Guarda as criptomoedas cadastradas (`id`, `simbolo`, `nome`).
   - Relacionamento **1:N** com `precos_cripto` e `investimentos`.
2. **`carteiras` (Classe `Carteira`):**
   - Guarda as carteiras/perfis de investidores (`id`, `nome`, `titular`, `perfil`, `data_criacao`).
   - Relacionamento **1:N** com `investimentos`.
3. **`precos_cripto` (Classe `PrecoCripto`):**
   - Guarda o histórico de cotações consultadas na Coinbase (`id`, `moeda_id [FK]`, `simbolo`, `preco`, `data_consulta`).
   - Relacionamento **N:1** com a tabela `moedas`.
4. **`investimentos` (Classe `Investimento`):**
   - Guarda as compras simuladas (`id`, `carteira_id [FK]`, `moeda_id [FK]`, `simbolo`, `valor_investido`, `preco_na_compra`, `quantidade_cripto`, `data_compra`).
   - Relacionamento **N:1** com `carteiras` e **N:1** com `moedas`.

---

## Operações CRUD Implementadas

Todas as 4 tabelas possuem suporte a **Create, Read, Update e Delete** tanto pelo **Menu de Terminal (`terminal.py`)** quanto pelas **Rotas da API (`routes.py`)**:

| Tabela | Create (Criar) | Read (Ler/Consultar) | Update (Editar) | Delete (Excluir) |
| :--- | :--- | :--- | :--- | :--- |
| **`moedas`** | Cadastrar nova cripto (ex: `ADA`, `DOGE`) | Listar moedas cadastradas | Editar nome da moeda | Remover moeda |
| **`carteiras`** | Criar nova carteira de cliente | Listar carteiras e total de compras | Editar nome, titular ou perfil | Excluir carteira |
| **`precos_cripto`** | Consultar Coinbase e gravar cotação | Termômetro (máx, mín, média) e histórico | Corrigir preço de uma cotação | Excluir cotação do histórico |
| **`investimentos`** | Simular compra em R$ | Listar compras e calcular lucro/prejuízo | Editar valor investido / carteira | Vender / excluir compra |

---

## Como Executar a Aplicação

### Pré-requisitos
- [Python 3.10+](https://www.python.org/downloads/) *(com "Add Python to PATH" marcado)*
- [Node.js 18+](https://nodejs.org/) *(necessário apenas para a interface Web)*

---

### Modo 1 — Executar o Menu Interativo no Terminal (CMD)

#### Pelo atalho automático (Windows):
Basta dar dois cliques em **`iniciar_terminal.bat`**. Ele prepara a `venv`, instala as bibliotecas do `requirements.txt` se necessário e abre o menu interativo no terminal.

#### Manualmente pelo terminal:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python terminal.py
```

No menu do terminal, escolha as opções de `1` a `5` para realizar o CRUD completo nas 4 tabelas ou `0` para sair com segurança.

---

### Modo 2 — Executar a API + Interface Web (Flask + React)

#### Pelo atalho automático (Windows):
Dê dois cliques em **`iniciar_projeto.bat`**. Ele instala as dependências automaticamente, inicia a API Flask na porta `5000` e abre o site React em `http://localhost:5173`.

---

## Principais Endpoints REST da API (`http://127.0.0.1:5000/api`)

| Método | Rota | Operação CRUD / Descrição |
| :--- | :--- | :--- |
| `GET` / `POST` | `/api/moedas` | **[READ / CREATE]** Lista ou cadastra criptomoedas |
| `PUT` / `DELETE` | `/api/moedas/<id>` | **[UPDATE / DELETE]** Atualiza ou remove uma criptomoeda |
| `GET` / `POST` | `/api/carteiras` | **[READ / CREATE]** Lista ou cria carteiras de investidores |
| `PUT` / `DELETE` | `/api/carteiras/<id>` | **[UPDATE / DELETE]** Edita ou remove uma carteira |
| `GET` | `/api/cripto/<moeda>` | **[CREATE + READ]** Busca preço na Coinbase, grava em `precos_cripto` e retorna o Termômetro |
| `GET` | `/api/cripto/historico` | **[READ]** Lista o histórico de cotações salvas |
| `PUT` / `DELETE` | `/api/cripto/historico/<id>` | **[UPDATE / DELETE]** Edita ou exclui uma cotação do histórico |
| `GET` | `/api/converter?moeda=btc&valor=100` | Converte valor em Reais (`R$`) para criptomoeda (e Satoshis) |
| `GET` / `POST` | `/api/carteira` | **[READ / CREATE]** Lista compras com lucro/prejuízo ou registra nova compra |
| `PUT` / `DELETE` | `/api/carteira/<id>` | **[UPDATE / DELETE]** Edita valor/carteira de uma compra ou realiza a venda |
