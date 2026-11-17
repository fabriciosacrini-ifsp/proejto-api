from flask import Blueprint, jsonify, request
from app.services import (
    atualizar_carteira,
    atualizar_cotacao_historico,
    atualizar_investimento,
    atualizar_moeda,
    cadastrar_moeda,
    converter_valor,
    criar_carteira,
    criar_investimento,
    listar_carteira,
    listar_carteiras,
    listar_historico,
    listar_moedas_db,
    obter_resumo_moeda,
    registrar_cotacao,
    remover_carteira,
    remover_cotacao_historico,
    remover_investimento,
    remover_moeda,
)

api_bp = Blueprint('api', __name__)


def _status_por_erro(mensagem: str) -> int:
    """Define o código HTTP adequado de acordo com o tipo de erro."""
    if "Coinbase" in mensagem:
        return 502
    if "não encontrad" in mensagem or "Nenhuma cotação" in mensagem:
        return 404
    return 400


def _converter_para_float(valor_bruto) -> float | None:
    """Converte texto ou número (aceitando vírgula) em float; retorna None se for inválido."""
    try:
        return float(str(valor_bruto).replace(',', '.'))
    except ValueError:
        return None


# =====================================================================
# ROTAS DA TABELA 1: MOEDAS (CRUD COMPLETO)
# =====================================================================

@api_bp.route('/moedas', methods=['GET'])
def get_moedas():
    """[READ] Lista todas as criptomoedas cadastradas no banco SQLite."""
    moedas = listar_moedas_db()
    return jsonify({
        "sucesso": True,
        "criptomoedas": [m.to_dict() for m in moedas],
    }), 200


@api_bp.route('/moedas', methods=['POST'])
def post_moeda():
    """[CREATE] Cadastra uma nova criptomoeda na tabela 'moedas'."""
    body = request.get_json(silent=True) or {}
    moeda, erro = cadastrar_moeda(body.get('simbolo', ''), body.get('nome', ''))
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Moeda cadastrada com sucesso",
        "dados": moeda.to_dict(),
    }), 201


@api_bp.route('/moedas/<int:moeda_id>', methods=['PUT'])
def put_moeda(moeda_id):
    """[UPDATE] Atualiza o nome de uma criptomoeda pelo ID."""
    body = request.get_json(silent=True) or {}
    moeda, erro = atualizar_moeda(moeda_id, body.get('nome', ''))
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Moeda atualizada com sucesso",
        "dados": moeda.to_dict(),
    }), 200


@api_bp.route('/moedas/<int:moeda_id>', methods=['DELETE'])
def delete_moeda(moeda_id):
    """[DELETE] Remove uma criptomoeda pelo ID."""
    ok, erro = remover_moeda(moeda_id)
    if not ok:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({"sucesso": True, "mensagem": "Moeda removida com sucesso"}), 200


# =====================================================================
# ROTAS DA TABELA 2: CARTEIRAS DE INVESTIDORES (CRUD COMPLETO)
# =====================================================================

@api_bp.route('/carteiras', methods=['GET'])
def get_carteiras():
    """[READ] Lista todas as carteiras cadastradas na tabela 'carteiras'."""
    carteiras = listar_carteiras()
    return jsonify({
        "sucesso": True,
        "total": len(carteiras),
        "dados": [c.to_dict() for c in carteiras],
    }), 200


@api_bp.route('/carteiras', methods=['POST'])
def post_carteiras():
    """[CREATE] Cria uma nova carteira de investidor."""
    body = request.get_json(silent=True) or {}
    carteira, erro = criar_carteira(
        nome=body.get('nome', ''),
        titular=body.get('titular', ''),
        perfil=body.get('perfil', 'Moderado'),
    )
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Carteira criada com sucesso",
        "dados": carteira.to_dict(),
    }), 201


@api_bp.route('/carteiras/<int:carteira_id>', methods=['PUT'])
def put_carteiras(carteira_id):
    """[UPDATE] Atualiza nome, titular ou perfil de uma carteira pelo ID."""
    body = request.get_json(silent=True) or {}
    carteira, erro = atualizar_carteira(
        carteira_id=carteira_id,
        novo_nome=body.get('nome'),
        novo_titular=body.get('titular'),
        novo_perfil=body.get('perfil'),
    )
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Carteira atualizada com sucesso",
        "dados": carteira.to_dict(),
    }), 200


@api_bp.route('/carteiras/<int:carteira_id>', methods=['DELETE'])
def delete_carteiras(carteira_id):
    """[DELETE] Exclui uma carteira pelo ID."""
    ok, erro = remover_carteira(carteira_id)
    if not ok:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({"sucesso": True, "mensagem": "Carteira removida com sucesso"}), 200


# =====================================================================
# ROTAS DA TABELA 3: COTAÇÕES / TERMÔMETRO (CRUD COMPLETO)
# =====================================================================

@api_bp.route('/cripto/<string:moeda>', methods=['GET'])
def get_cripto(moeda):
    """[CREATE + READ] Busca cotação na Coinbase, grava em 'precos_cripto' e devolve o termômetro."""
    registro, termometro, erro = registrar_cotacao(moeda)

    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Preço atualizado e gravado com sucesso",
        "dados": registro.to_dict(),
        "termometro": termometro,
    }), 200


@api_bp.route('/cripto/<string:moeda>/resumo', methods=['GET'])
def get_cripto_resumo(moeda):
    """[READ] Consulta apenas o termômetro salvo no banco sem gravar nova cotação."""
    termometro, erro = obter_resumo_moeda(moeda)

    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "termometro": termometro,
    }), 200


@api_bp.route('/cripto/historico', methods=['GET'])
def get_historico():
    """[READ] Lista o histórico salvo no banco (aceita filtro opcional ?moeda=btc)."""
    moeda = request.args.get('moeda')
    registros = listar_historico(moeda)

    return jsonify({
        "sucesso": True,
        "total": len(registros),
        "dados": [r.to_dict() for r in registros],
    }), 200


@api_bp.route('/cripto/historico/<int:cotacao_id>', methods=['PUT'])
def put_historico(cotacao_id):
    """[UPDATE] Corrige/atualiza o preço de uma cotação salva no histórico."""
    body = request.get_json(silent=True) or {}
    novo_preco = _converter_para_float(body.get('preco'))
    if novo_preco is None:
        return jsonify({"sucesso": False, "mensagem": "Informe um 'preco' numérico válido"}), 400

    registro, erro = atualizar_cotacao_historico(cotacao_id, novo_preco)
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Cotação atualizada com sucesso",
        "dados": registro.to_dict(),
    }), 200


@api_bp.route('/cripto/historico/<int:cotacao_id>', methods=['DELETE'])
def delete_historico(cotacao_id):
    """[DELETE] Remove um registro específico do histórico de cotações."""
    ok, erro = remover_cotacao_historico(cotacao_id)
    if not ok:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({"sucesso": True, "mensagem": "Cotação excluída do histórico"}), 200


# =====================================================================
# ROTA DO CONVERSOR DE MOEDAS
# =====================================================================

@api_bp.route('/converter', methods=['GET'])
def get_converter():
    """Converte um valor em Reais (BRL) para cripto. Ex: /api/converter?moeda=btc&valor=100"""
    moeda = request.args.get('moeda', '')
    valor_texto = request.args.get('valor') or request.args.get('reais')

    if not moeda or not valor_texto:
        return jsonify({
            "sucesso": False,
            "mensagem": "Informe os parâmetros 'moeda' e 'valor' na URL (ex: ?moeda=btc&valor=100)",
        }), 400

    valor = _converter_para_float(valor_texto)
    if valor is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "O campo 'valor' precisa ser um número válido",
        }), 400

    resultado, erro = converter_valor(moeda, valor)
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "dados": resultado,
    }), 200


# =====================================================================
# ROTAS DA TABELA 4: INVESTIMENTOS DA CARTEIRA VIRTUAL (CRUD COMPLETO)
# =====================================================================

@api_bp.route('/carteira', methods=['GET'])
def get_carteira():
    """[READ] Lista os investimentos da Carteira Virtual (aceita ?moeda=btc&atualizar=1)."""
    moeda = request.args.get('moeda')
    forcar = request.args.get('atualizar') == '1'
    carteira_id = request.args.get('carteira_id', type=int)

    itens, resumo = listar_carteira(moeda, forcar_atualizacao=forcar, carteira_id=carteira_id)

    return jsonify({
        "sucesso": True,
        "total_itens": len(itens),
        "resumo": resumo,
        "dados": itens,
    }), 200


@api_bp.route('/carteira', methods=['POST'])
def post_carteira():
    """[CREATE] Registra uma compra simulada em BRL na Carteira Virtual."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie um objeto JSON válido com 'moeda' e 'valor_investido'",
        }), 400

    moeda = body.get('moeda', '')
    valor_bruto = body.get('valor_investido')
    carteira_id = body.get('carteira_id', 1)

    if not moeda or valor_bruto is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie 'moeda' e 'valor_investido' no corpo JSON",
        }), 400

    valor_investido = _converter_para_float(valor_bruto)
    if valor_investido is None:
        return jsonify({
            "sucesso": False,
            "mensagem": "O campo 'valor_investido' precisa ser um número válido",
        }), 400

    investimento, erro = criar_investimento(moeda, valor_investido, carteira_id=int(carteira_id))
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Compra simulada registrada na carteira com sucesso",
        "dados": investimento.to_dict(),
    }), 201


@api_bp.route('/carteira/<int:investimento_id>', methods=['PUT'])
def put_carteira(investimento_id):
    """[UPDATE] Atualiza o valor investido e/ou a carteira vinculada de uma compra pelo ID."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"sucesso": False, "mensagem": "Envie um objeto JSON válido"}), 400

    novo_valor = None
    if 'valor_investido' in body:
        novo_valor = _converter_para_float(body.get('valor_investido'))
        if novo_valor is None:
            return jsonify({
                "sucesso": False,
                "mensagem": "O campo 'valor_investido' precisa ser um número válido",
            }), 400

    nova_carteira_id = body.get('carteira_id')
    if nova_carteira_id is not None:
        try:
            nova_carteira_id = int(nova_carteira_id)
        except ValueError:
            return jsonify({"sucesso": False, "mensagem": "'carteira_id' deve ser inteiro"}), 400

    investimento, erro = atualizar_investimento(
        investimento_id,
        novo_valor_investido=novo_valor,
        nova_carteira_id=nova_carteira_id,
    )
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Investimento atualizado com sucesso",
        "dados": investimento.to_dict(),
    }), 200


@api_bp.route('/carteira/<int:investimento_id>', methods=['DELETE'])
def delete_carteira(investimento_id):
    """[DELETE] Remove (simula a venda) de um investimento da carteira pelo ID."""
    ok, erro = remover_investimento(investimento_id)
    if not ok:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Investimento removido da carteira com sucesso",
    }), 200
