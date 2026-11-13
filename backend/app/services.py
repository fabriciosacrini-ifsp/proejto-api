import math
import time
import requests
from app import db
from app.models import PrecoCripto, Investimento

# Criptomoedas aceitas pela nossa API (chave da URL -> nome completo)
MOEDAS_SUPORTADAS = {
    "btc": "Bitcoin",
    "eth": "Ethereum",
    "link": "Chainlink",
    "sol": "Solana",
}

# Moeda fixa do sistema: sempre em Reais (BRL)
MOEDA_PADRAO = "BRL"

# Guarda o último preço por 5 segundos para evitar diferença de centavos ao comprar
_CACHE_PRECOS = {}
TEMPO_CACHE_SEGUNDOS = 5


def arredondar(valor: float, casas: int = 2) -> float:
    """Arredonda um número e evita que apareça -0.0."""
    resultado = round(valor, casas)
    return 0.0 if abs(resultado) == 0 else resultado


def validar_moeda(moeda_key: str):
    """Verifica se a criptomoeda enviada existe em MOEDAS_SUPORTADAS."""
    if not isinstance(moeda_key, str) or not moeda_key.strip():
        return None, "Informe uma criptomoeda válida"

    moeda_limpa = moeda_key.strip().lower()
    if moeda_limpa not in MOEDAS_SUPORTADAS:
        return None, "Moeda não suportada"

    return moeda_limpa, None


def consultar_preco_coinbase(simbolo: str, usar_cache: bool = True) -> float | None:
    """Busca o preço atual da criptomoeda em Reais (BRL) na API pública da Coinbase."""
    par = f"{simbolo.upper()}-{MOEDA_PADRAO}"
    agora = time.time()

    if usar_cache and par in _CACHE_PRECOS:
        preco_salvo, momento = _CACHE_PRECOS[par]
        if agora - momento <= TEMPO_CACHE_SEGUNDOS:
            return preco_salvo

    url = f"https://api.coinbase.com/v2/prices/{par}/spot"

    try:
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            preco = float(resposta.json()["data"]["amount"])
            _CACHE_PRECOS[par] = (preco, agora)
            return preco
    except requests.RequestException:
        return None

    return None


def calcular_termometro(simbolo: str) -> dict | None:
    """
    Lê o histórico salvo no banco para aquela moeda e calcula:
    - se subiu, caiu ou manteve em relação à consulta anterior;
    - maior preço, menor preço e média.
    """
    # Ordena do mais recente para o mais antigo: [0] é o atual e [1] é o anterior
    registros = (
        PrecoCripto.query
        .filter_by(simbolo=simbolo.upper(), moeda_base=MOEDA_PADRAO)
        .order_by(PrecoCripto.data_consulta.desc(), PrecoCripto.id.desc())
        .all()
    )

    if not registros:
        return None

    precos = [r.preco for r in registros]
    preco_atual = registros[0].preco

    if len(registros) >= 2:
        preco_anterior = registros[1].preco
        diferenca = arredondar(preco_atual - preco_anterior, 2)
        variacao_percentual = (
            arredondar((diferenca / preco_anterior) * 100, 2)
            if preco_anterior > 0
            else 0.0
        )

        if diferenca > 0:
            tendencia = "SUBIU"
        elif diferenca < 0:
            tendencia = "CAIU"
        else:
            tendencia = "MANTEVE"
    else:
        preco_anterior = None
        diferenca = 0.0
        variacao_percentual = 0.0
        tendencia = "PRIMEIRA_CONSULTA"

    return {
        "simbolo": simbolo.upper(),
        "preco_atual": arredondar(preco_atual, 2),
        "preco_anterior": arredondar(preco_anterior, 2) if preco_anterior is not None else None,
        "diferenca": diferenca,
        "variacao_percentual": variacao_percentual,
        "tendencia": tendencia,
        "maior_preco": arredondar(max(precos), 2),
        "menor_preco": arredondar(min(precos), 2),
        "media_preco": arredondar(sum(precos) / len(precos), 2),
        "total_consultas": len(registros),
    }


def registrar_cotacao(moeda_key: str):
    """Consulta o preço ao vivo na Coinbase, grava no SQLite e devolve o termômetro."""
    moeda_limpa, erro = validar_moeda(moeda_key)
    if erro:
        return None, None, erro

    preco = consultar_preco_coinbase(moeda_limpa, usar_cache=False)
    if preco is None:
        return None, None, "Falha ao obter cotação na Coinbase"

    novo_registro = PrecoCripto(
        simbolo=moeda_limpa.upper(),
        moeda_base=MOEDA_PADRAO,
        preco=preco,
    )
    db.session.add(novo_registro)
    db.session.commit()

    termometro = calcular_termometro(moeda_limpa)
    return novo_registro, termometro, None


def obter_resumo_moeda(moeda_key: str):
    """Retorna apenas o termômetro já salvo no banco, sem gravar uma nova consulta."""
    moeda_limpa, erro = validar_moeda(moeda_key)
    if erro:
        return None, erro

    termometro = calcular_termometro(moeda_limpa)
    if termometro is None:
        return None, "Nenhuma cotação registrada ainda para esta moeda"

    return termometro, None


def listar_historico(moeda_key: str | None = None):
    """Lista todas as cotações salvas no banco para a moeda informada."""
    query = PrecoCripto.query.filter_by(moeda_base=MOEDA_PADRAO)

    if moeda_key:
        query = query.filter_by(simbolo=moeda_key.strip().upper())

    return query.order_by(PrecoCripto.data_consulta.desc(), PrecoCripto.id.desc()).all()


def _validar_valor_positivo(valor: float, mensagem_erro: str) -> str | None:
    """Garante que o valor numérico é finito e maior que zero."""
    if not math.isfinite(valor) or valor <= 0:
        return mensagem_erro
    return None


def converter_valor(moeda_key: str, valor: float):
    """Converte um valor em Reais (R$) para a fração correspondente da criptomoeda."""
    moeda_limpa, erro = validar_moeda(moeda_key)
    if erro:
        return None, erro

    erro_valor = _validar_valor_positivo(valor, "O valor para conversão deve ser maior que zero")
    if erro_valor:
        return None, erro_valor

    preco_unitario = consultar_preco_coinbase(moeda_limpa)
    if preco_unitario is None:
        return None, "Falha ao obter cotação na Coinbase"

    quantidade_cripto = valor / preco_unitario

    resultado = {
        "moeda": moeda_limpa.upper(),
        "nome_moeda": MOEDAS_SUPORTADAS[moeda_limpa],
        "valor_informado": arredondar(valor, 2),
        "preco_unitario": arredondar(preco_unitario, 2),
        "quantidade_cripto": round(quantidade_cripto, 8),
    }

    # 1 Bitcoin equivale a 100 milhões de Satoshis
    if moeda_limpa == "btc":
        resultado["satoshis"] = round(quantidade_cripto * 100_000_000)

    return resultado, None


def criar_investimento(moeda_key: str, valor_investido: float):
    """Simula a compra de uma criptomoeda em Reais e salva na tabela Investimento."""
    moeda_limpa, erro = validar_moeda(moeda_key)
    if erro:
        return None, erro

    erro_valor = _validar_valor_positivo(valor_investido, "O valor investido deve ser maior que zero")
    if erro_valor:
        return None, erro_valor

    preco_na_compra = consultar_preco_coinbase(moeda_limpa)
    if preco_na_compra is None:
        return None, "Falha ao obter cotação na Coinbase"

    quantidade_cripto = valor_investido / preco_na_compra

    novo_investimento = Investimento(
        simbolo=moeda_limpa.upper(),
        moeda_base=MOEDA_PADRAO,
        valor_investido=valor_investido,
        preco_na_compra=preco_na_compra,
        quantidade_cripto=quantidade_cripto,
    )
    db.session.add(novo_investimento)
    db.session.commit()

    return novo_investimento, None


def _calcular_item_carteira(inv: Investimento, preco_atual: float | None) -> dict:
    """Calcula quanto uma compra antiga vale hoje e se está dando lucro ou prejuízo."""
    dados_item = inv.to_dict()

    if preco_atual is None:
        dados_item.update({
            "cotacao_disponivel": False,
            "preco_atual": None,
            "valor_atual": None,
            "lucro_prejuizo": None,
            "variacao_percentual": None,
            "status": "INDISPONIVEL",
        })
        return dados_item

    if round(preco_atual, 2) == round(inv.preco_na_compra, 2):
        valor_atual = arredondar(inv.valor_investido, 2)
        lucro_prejuizo = 0.0
        variacao_percentual = 0.0
    else:
        valor_atual = arredondar(inv.quantidade_cripto * preco_atual, 2)
        lucro_prejuizo = arredondar(valor_atual - inv.valor_investido, 2)
        variacao_percentual = (
            arredondar((lucro_prejuizo / inv.valor_investido) * 100, 2)
            if inv.valor_investido > 0
            else 0.0
        )

    if lucro_prejuizo > 0:
        status = "LUCRO"
    elif lucro_prejuizo < 0:
        status = "PREJUIZO"
    else:
        status = "EMPATE"

    dados_item.update({
        "cotacao_disponivel": True,
        "preco_atual": arredondar(preco_atual, 2),
        "valor_atual": valor_atual,
        "lucro_prejuizo": lucro_prejuizo,
        "variacao_percentual": variacao_percentual,
        "status": status,
    })
    return dados_item


def listar_carteira(moeda_key: str | None = None, forcar_atualizacao: bool = False):
    """
    Lista as compras da moeda escolhida e soma:
    - quantidade_total_cripto (fração total acumulada);
    - total_investido, total_atual e lucro_prejuizo_total.
    """
    query = Investimento.query.filter_by(moeda_base=MOEDA_PADRAO)

    if moeda_key:
        query = query.filter_by(simbolo=moeda_key.strip().upper())

    investimentos = query.order_by(
        Investimento.data_compra.desc(), Investimento.id.desc()
    ).all()

    # Consulta a Coinbase apenas 1 vez por moeda diferente
    cotacoes_atuais = {}
    for inv in investimentos:
        if inv.simbolo not in cotacoes_atuais:
            cotacoes_atuais[inv.simbolo] = consultar_preco_coinbase(
                inv.simbolo,
                usar_cache=not forcar_atualizacao,
            )

    itens = []
    quantidade_total = 0.0
    total_investido = 0.0
    total_atual = 0.0

    for inv in investimentos:
        preco_atual = cotacoes_atuais.get(inv.simbolo)
        dados_item = _calcular_item_carteira(inv, preco_atual)
        itens.append(dados_item)

        if dados_item["cotacao_disponivel"]:
            quantidade_total += inv.quantidade_cripto
            total_investido += inv.valor_investido
            total_atual += dados_item["valor_atual"]

    resumo = None
    if total_investido > 0:
        investido = arredondar(total_investido, 2)
        atual = arredondar(total_atual, 2)
        lucro = arredondar(atual - investido, 2)
        variacao = arredondar((lucro / investido) * 100, 2)

        resumo = {
            "quantidade_total_cripto": round(quantidade_total, 8),
            "total_investido": investido,
            "total_atual": atual,
            "lucro_prejuizo_total": lucro,
            "variacao_total_percentual": variacao,
        }

    return itens, resumo


def remover_investimento(investimento_id: int):
    """Remove (simula a venda) de um investimento da Carteira Virtual pelo ID."""
    investimento = db.session.get(Investimento, investimento_id)
    if investimento is None:
        return False, "Investimento não encontrado"

    db.session.delete(investimento)
    db.session.commit()
    return True, None
