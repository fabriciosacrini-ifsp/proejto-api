import math
import time
import requests
from app import db
from app.models import Moeda, Carteira, PrecoCripto, Investimento

# Criptomoedas iniciais do sistema (cadastradas automaticamente no SQLite)
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


def _validar_valor_positivo(valor: float, mensagem_erro: str) -> str | None:
    """Garante que o valor numérico é finito e maior que zero."""
    if not math.isfinite(valor) or valor <= 0:
        return mensagem_erro
    return None


def inicializar_dados_padrao():
    """
    Popula o banco SQLite com as 4 moedas iniciais e a Carteira Principal
    caso o banco esteja vazio na primeira execução.
    """
    for sigla, nome in MOEDAS_SUPORTADAS.items():
        simbolo_upper = sigla.upper()
        existe = Moeda.query.filter_by(simbolo=simbolo_upper).first()
        if not existe:
            db.session.add(Moeda(simbolo=simbolo_upper, nome=nome))

    carteira_padrao = Carteira.query.first()
    if not carteira_padrao:
        db.session.add(
            Carteira(
                nome="Carteira Principal",
                titular="Investidor Padrão",
                perfil="Moderado",
            )
        )

    db.session.commit()


def buscar_moeda_db(moeda_key: str) -> tuple[Moeda | None, str | None]:
    """Busca a criptomoeda na tabela 'moedas' pela sigla (ex: 'btc' ou 'BTC')."""
    if not isinstance(moeda_key, str) or not moeda_key.strip():
        return None, "Informe uma criptomoeda válida"

    simbolo = moeda_key.strip().upper()
    moeda_obj = Moeda.query.filter_by(simbolo=simbolo).first()

    if not moeda_obj:
        return None, f"Moeda '{simbolo}' não encontrada no cadastro"

    return moeda_obj, None


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


# =====================================================================
# CRUD TABELA 1: MOEDAS (moedas)
# =====================================================================

def listar_moedas_db() -> list[Moeda]:
    """[READ] Lista todas as criptomoedas cadastradas na tabela 'moedas'."""
    return Moeda.query.order_by(Moeda.id.asc()).all()


def cadastrar_moeda(simbolo: str, nome: str):
    """[CREATE] Cadastra uma nova criptomoeda após validar se existe na Coinbase."""
    if not simbolo or not simbolo.strip() or not nome or not nome.strip():
        return None, "Informe o símbolo (ex: ADA) e o nome da moeda (ex: Cardano)"

    simbolo_limpo = simbolo.strip().upper()
    nome_limpo = nome.strip()

    if Moeda.query.filter_by(simbolo=simbolo_limpo).first():
        return None, f"A moeda '{simbolo_limpo}' já está cadastrada"

    preco_teste = consultar_preco_coinbase(simbolo_limpo, usar_cache=False)
    if preco_teste is None:
        return None, f"A Coinbase não possui cotação em BRL para '{simbolo_limpo}'"

    nova_moeda = Moeda(simbolo=simbolo_limpo, nome=nome_limpo)
    db.session.add(nova_moeda)
    db.session.commit()
    return nova_moeda, None


def atualizar_moeda(moeda_id: int, novo_nome: str):
    """[UPDATE] Atualiza o nome de uma criptomoeda cadastrada."""
    moeda_obj = db.session.get(Moeda, moeda_id)
    if not moeda_obj:
        return None, "Moeda não encontrada pelo ID informado"

    if not novo_nome or not novo_nome.strip():
        return None, "Informe um novo nome válido para a moeda"

    moeda_obj.nome = novo_nome.strip()
    db.session.commit()
    return moeda_obj, None


def remover_moeda(moeda_id: int):
    """[DELETE] Remove uma criptomoeda e seus registros vinculados."""
    moeda_obj = db.session.get(Moeda, moeda_id)
    if not moeda_obj:
        return False, "Moeda não encontrada pelo ID informado"

    if Moeda.query.count() <= 1:
        return False, "Não é permitido excluir a última moeda do sistema"

    db.session.delete(moeda_obj)
    db.session.commit()
    return True, None


# =====================================================================
# CRUD TABELA 2: CARTEIRAS (carteiras)
# =====================================================================

def listar_carteiras() -> list[Carteira]:
    """[READ] Lista todas as carteiras de investidores cadastradas."""
    return Carteira.query.order_by(Carteira.id.asc()).all()


def criar_carteira(nome: str, titular: str, perfil: str = "Moderado"):
    """[CREATE] Cria uma nova carteira de investimentos no banco."""
    if not nome or not nome.strip() or not titular or not titular.strip():
        return None, "Informe o nome da carteira e o nome do titular"

    perfil_limpo = (perfil or "Moderado").strip().capitalize()
    nova_carteira = Carteira(
        nome=nome.strip(),
        titular=titular.strip(),
        perfil=perfil_limpo,
    )
    db.session.add(nova_carteira)
    db.session.commit()
    return nova_carteira, None


def atualizar_carteira(
    carteira_id: int,
    novo_nome: str | None = None,
    novo_titular: str | None = None,
    novo_perfil: str | None = None,
):
    """[UPDATE] Atualiza os dados cadastrais (nome, titular ou perfil) de uma carteira."""
    carteira = db.session.get(Carteira, carteira_id)
    if not carteira:
        return None, "Carteira não encontrada pelo ID informado"

    if novo_nome is not None and novo_nome.strip():
        carteira.nome = novo_nome.strip()
    if novo_titular is not None and novo_titular.strip():
        carteira.titular = novo_titular.strip()
    if novo_perfil is not None and novo_perfil.strip():
        carteira.perfil = novo_perfil.strip().capitalize()

    db.session.commit()
    return carteira, None


def remover_carteira(carteira_id: int):
    """[DELETE] Exclui uma carteira e suas compras vinculadas."""
    carteira = db.session.get(Carteira, carteira_id)
    if not carteira:
        return False, "Carteira não encontrada pelo ID informado"

    if Carteira.query.count() <= 1:
        return False, "Não é permitido excluir a única carteira ativa do sistema"

    db.session.delete(carteira)
    db.session.commit()
    return True, None


# =====================================================================
# CRUD TABELA 3: COTAÇÕES / TERMÔMETRO (precos_cripto)
# =====================================================================

def calcular_termometro(simbolo: str) -> dict | None:
    """
    Lê o histórico salvo no banco para aquela moeda e calcula:
    - se subiu, caiu ou manteve em relação à consulta anterior;
    - maior preço, menor preço e média.
    """
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
    """[CREATE] Consulta o preço ao vivo na Coinbase, grava em 'precos_cripto' e devolve o termômetro."""
    moeda_obj, erro = buscar_moeda_db(moeda_key)
    if erro:
        return None, None, erro

    preco = consultar_preco_coinbase(moeda_obj.simbolo, usar_cache=False)
    if preco is None:
        return None, None, "Falha ao obter cotação na Coinbase"

    novo_registro = PrecoCripto(
        moeda_id=moeda_obj.id,
        simbolo=moeda_obj.simbolo,
        moeda_base=MOEDA_PADRAO,
        preco=preco,
    )
    db.session.add(novo_registro)
    db.session.commit()

    termometro = calcular_termometro(moeda_obj.simbolo)
    return novo_registro, termometro, None


def obter_resumo_moeda(moeda_key: str):
    """[READ] Retorna apenas o termômetro já salvo no banco, sem gravar nova consulta."""
    moeda_obj, erro = buscar_moeda_db(moeda_key)
    if erro:
        return None, erro

    termometro = calcular_termometro(moeda_obj.simbolo)
    if termometro is None:
        return None, "Nenhuma cotação registrada ainda para esta moeda"

    return termometro, None


def listar_historico(moeda_key: str | None = None):
    """[READ] Lista todas as cotações salvas no banco (opcionalmente filtrando por moeda)."""
    query = PrecoCripto.query.filter_by(moeda_base=MOEDA_PADRAO)

    if moeda_key:
        query = query.filter_by(simbolo=moeda_key.strip().upper())

    return query.order_by(PrecoCripto.data_consulta.desc(), PrecoCripto.id.desc()).all()


def atualizar_cotacao_historico(cotacao_id: int, novo_preco: float):
    """[UPDATE] Corrige/atualiza o preço em Reais de uma cotação já salva no histórico."""
    registro = db.session.get(PrecoCripto, cotacao_id)
    if not registro:
        return None, "Registro de cotação não encontrado pelo ID informado"

    erro_valor = _validar_valor_positivo(novo_preco, "O novo preço deve ser maior que zero")
    if erro_valor:
        return None, erro_valor

    registro.preco = novo_preco
    db.session.commit()
    return registro, None


def remover_cotacao_historico(cotacao_id: int):
    """[DELETE] Remove um registro específico do histórico de cotações pelo ID."""
    registro = db.session.get(PrecoCripto, cotacao_id)
    if not registro:
        return False, "Registro de cotação não encontrado pelo ID informado"

    db.session.delete(registro)
    db.session.commit()
    return True, None


# =====================================================================
# CONVERSOR DE MOEDAS (BRL -> CRIPTO / SATOSHIS)
# =====================================================================

def converter_valor(moeda_key: str, valor: float):
    """Converte um valor em Reais (R$) para a fração correspondente da criptomoeda."""
    moeda_obj, erro = buscar_moeda_db(moeda_key)
    if erro:
        return None, erro

    erro_valor = _validar_valor_positivo(valor, "O valor para conversão deve ser maior que zero")
    if erro_valor:
        return None, erro_valor

    preco_unitario = consultar_preco_coinbase(moeda_obj.simbolo)
    if preco_unitario is None:
        return None, "Falha ao obter cotação na Coinbase"

    quantidade_cripto = valor / preco_unitario

    resultado = {
        "moeda": moeda_obj.simbolo,
        "nome_moeda": moeda_obj.nome,
        "valor_informado": arredondar(valor, 2),
        "preco_unitario": arredondar(preco_unitario, 2),
        "quantidade_cripto": round(quantidade_cripto, 8),
    }

    # 1 Bitcoin equivale a 100 milhões de Satoshis
    if moeda_obj.simbolo == "BTC":
        resultado["satoshis"] = round(quantidade_cripto * 100_000_000)

    return resultado, None


# =====================================================================
# CRUD TABELA 4: INVESTIMENTOS DA CARTEIRA (investimentos)
# =====================================================================

def criar_investimento(moeda_key: str, valor_investido: float, carteira_id: int = 1):
    """[CREATE] Simula a compra de uma criptomoeda em Reais vinculada a uma Carteira e uma Moeda."""
    moeda_obj, erro = buscar_moeda_db(moeda_key)
    if erro:
        return None, erro

    erro_valor = _validar_valor_positivo(valor_investido, "O valor investido deve ser maior que zero")
    if erro_valor:
        return None, erro_valor

    carteira_obj = db.session.get(Carteira, carteira_id)
    if not carteira_obj:
        # Se a carteira 1 não existir por qualquer motivo, usa a primeira disponível
        carteira_obj = Carteira.query.first()
        if not carteira_obj:
            return None, "Carteira não encontrada no banco de dados"

    preco_na_compra = consultar_preco_coinbase(moeda_obj.simbolo)
    if preco_na_compra is None:
        return None, "Falha ao obter cotação na Coinbase"

    quantidade_cripto = valor_investido / preco_na_compra

    novo_investimento = Investimento(
        carteira_id=carteira_obj.id,
        moeda_id=moeda_obj.id,
        simbolo=moeda_obj.simbolo,
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


def listar_carteira(
    moeda_key: str | None = None,
    forcar_atualizacao: bool = False,
    carteira_id: int | None = None,
):
    """
    [READ] Lista as compras salvas (filtrando opcionalmente por moeda e/ou carteira)
    e calcula o resumo financeiro atualizado.
    """
    query = Investimento.query.filter_by(moeda_base=MOEDA_PADRAO)

    if moeda_key:
        query = query.filter_by(simbolo=moeda_key.strip().upper())

    if carteira_id is not None:
        query = query.filter_by(carteira_id=carteira_id)

    investimentos = query.order_by(
        Investimento.data_compra.desc(), Investimento.id.desc()
    ).all()

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


def atualizar_investimento(
    investimento_id: int,
    novo_valor_investido: float | None = None,
    nova_carteira_id: int | None = None,
):
    """
    [UPDATE] Atualiza o valor investido (recalculando a fração de cripto)
    e/ou transfere o investimento para outra carteira.
    """
    investimento = db.session.get(Investimento, investimento_id)
    if investimento is None:
        return None, "Investimento não encontrado pelo ID informado"

    if novo_valor_investido is not None:
        erro_valor = _validar_valor_positivo(
            novo_valor_investido,
            "O novo valor investido deve ser maior que zero",
        )
        if erro_valor:
            return None, erro_valor

        investimento.valor_investido = novo_valor_investido
        investimento.quantidade_cripto = novo_valor_investido / investimento.preco_na_compra

    if nova_carteira_id is not None:
        carteira_destino = db.session.get(Carteira, nova_carteira_id)
        if not carteira_destino:
            return None, "A carteira informada para transferência não existe"
        investimento.carteira_id = carteira_destino.id

    db.session.commit()
    return investimento, None


def remover_investimento(investimento_id: int):
    """[DELETE] Remove (simula a venda) de um investimento da Carteira Virtual pelo ID."""
    investimento = db.session.get(Investimento, investimento_id)
    if investimento is None:
        return False, "Investimento não encontrado pelo ID informado"

    db.session.delete(investimento)
    db.session.commit()
    return True, None
