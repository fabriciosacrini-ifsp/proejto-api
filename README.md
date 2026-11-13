# CriptoMonitor

Aplicação web full-stack para monitoramento de criptomoedas em tempo real em **Reais (BRL)**, utilizando a API pública da **Coinbase**, backend em **Python (Flask + SQLite)** e frontend em **React + Vite**.

---

## Funcionalidades

- **Termômetro de Cotação:** consulta a cotação atual na Coinbase (`BTC`, `ETH`, `LINK`, `SOL`), salva no banco de dados SQLite e exibe a variação em relação à consulta anterior, além de máxima, mínima, média e um pop-up com o histórico de consultas.
- **Conversor Instantâneo:** converte qualquer valor em Reais (`R$`) para a fração correspondente da criptomoeda selecionada (incluindo exibição em *Satoshis* para Bitcoin).
- **Carteira Virtual:** simula compras em `R$`, calcula automaticamente a quantidade acumulada, o valor atualizado hoje e o lucro/prejuízo, além de permitir visualizar e simular a venda de cada compra em um pop-up.
- **Tema Claro / Escuro:** alternância direta na interface.

---

## Tecnologias Utilizadas

- **Backend:** Python, Flask, Flask-SQLAlchemy, SQLite, Requests
- **Frontend:** React, Vite, Lucide React
- **API Externa:** Coinbase Spot Price API (`https://api.coinbase.com/v2/prices/{MOEDA}-BRL/spot`)

---

## Pré-requisitos

Para executar o projeto em um computador novo, é necessário ter instalado:
- [Python 3.10+](https://www.python.org/downloads/) *(marque a opção "Add Python to PATH" na instalação)*
- [Node.js 18+](https://nodejs.org/)

---

## Como Executar o Projeto

### Opção 1 — Automática (Windows, recomendado)

1. Baixe ou clone este repositório.
2. Dê dois cliques no arquivo **`iniciar_projeto.bat`** na pasta raiz.
3. Na primeira execução, o script cria automaticamente o ambiente virtual Python (`venv`), baixa as dependências do `requirements.txt` e do `package.json` (`node_modules`), inicia os dois servidores e abre o site no navegador em **`http://localhost:5173`**.

---

### Opção 2 — Manual (via Terminal)

#### 1. Iniciar o Backend (Porta `5000`)
```bash
cd backend
python -m venv venv

# No Windows:
venv\Scripts\activate
# No Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
python run.py
```

#### 2. Iniciar o Frontend (Porta `5173`)
Em outro terminal:
```bash
cd frontend
npm install
npm run dev -- --port 5173 --strictPort
```

Após iniciar os dois servidores, acesse **`http://localhost:5173`** no navegador.

---

## Estrutura do Projeto

```text
Projeto-API/
├── iniciar_projeto.bat       # Inicializador automático (Windows)
├── backend/                  # API Flask + Banco SQLite
│   ├── run.py                # Ponto de entrada do servidor Flask
│   ├── config.py             # Configuração do SQLite
│   ├── requirements.txt      # Dependências Python
│   └── app/
│       ├── __init__.py       # Criação do app Flask e liberação de CORS
│       ├── models.py         # Tabelas PrecoCripto e Investimento
│       ├── services.py       # Regras de negócio e chamadas à Coinbase
│       └── routes.py         # Rotas REST da API (/api/...)
└── frontend/                 # Interface React + Vite
    ├── package.json          # Dependências JavaScript
    └── src/
        ├── App.jsx           # Tela principal e controle de moeda/tema
        ├── services/api.js   # Comunicação com o backend Flask
        └── components/       # Termômetro, Conversor, Carteira e Modais
```

---

## Principais Endpoints da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/moedas` | Lista as criptomoedas suportadas (`BTC`, `ETH`, `LINK`, `SOL`) |
| `GET` | `/api/cripto/<moeda>` | Consulta a Coinbase, salva no SQLite e retorna o termômetro |
| `GET` | `/api/cripto/<moeda>/resumo` | Retorna o termômetro já salvo no banco |
| `GET` | `/api/cripto/historico?moeda=btc` | Lista o histórico de cotações salvas |
| `GET` | `/api/converter?moeda=btc&valor=100` | Converte um valor em `R$` para criptomoeda |
| `GET` | `/api/carteira?moeda=btc` | Lista compras simuladas e resumo de lucro/prejuízo |
| `POST` | `/api/carteira` | Registra uma nova compra simulada em `R$` |
| `DELETE` | `/api/carteira/<id>` | Remove (simula a venda) de uma compra |
