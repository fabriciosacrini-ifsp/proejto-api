from flask import Blueprint, jsonify, request
from app.services import (
    MOEDAS_SUPORTADAS,
    converter_valor,
    criar_investimento,
    listar_carteira,
    listar_historico,
    obter_resumo_moeda,
    registrar_cotacao,
    remover_investimento,
)

api_bp = Blueprint('api', __name__)


def _status_por_erro(mensagem: str) -> int:
    """Define o código HTTP adequado de acordo com o tipo de erro."""
    if "Coinbase" in mensagem:
        return 502
    if "não encontrado" in mensagem or "Nenhuma cotação" in mensagem:
        return 404
    return 400


def _converter_para_float(valor_bruto) -> float | None:
    """Converte texto ou número (aceitando vírgula) em float; retorna None se for inválido."""
    try:
        return float(str(valor_bruto).replace(',', '.'))
    except ValueError:
        return None


@api_bp.route('/moedas', methods=['GET'])
def get_moedas():
    """Lista todas as criptomoedas suportadas pela API."""
    criptos = [
        {"codigo": codigo.upper(), "chave": codigo, "nome": nome}
        for codigo, nome in MOEDAS_SUPORTADAS.items()
    ]
    return jsonify({
        "sucesso": True,
        "criptomoedas": criptos,
    }), 200


@api_bp.route('/cripto/<string:moeda>', methods=['GET'])
def get_cripto(moeda):
    """Busca a cotação em BRL na Coinbase, grava no banco e devolve junto com o termômetro."""
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
    """Consulta apenas o termômetro salvo no banco sem gravar nova cotação."""
    termometro, erro = obter_resumo_moeda(moeda)

    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "termometro": termometro,
    }), 200


@api_bp.route('/cripto/historico', methods=['GET'])
def get_historico():
    """Lista o histórico salvo no banco (aceita filtro opcional ?moeda=btc)."""
    moeda = request.args.get('moeda')
    registros = listar_historico(moeda)

    return jsonify({
        "sucesso": True,
        "total": len(registros),
        "dados": [r.to_dict() for r in registros],
    }), 200


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


@api_bp.route('/carteira', methods=['GET'])
def get_carteira():
    """Lista os investimentos da Carteira Virtual (aceita ?moeda=btc&atualizar=1)."""
    moeda = request.args.get('moeda')
    forcar = request.args.get('atualizar') == '1'

    itens, resumo = listar_carteira(moeda, forcar_atualizacao=forcar)

    return jsonify({
        "sucesso": True,
        "total_itens": len(itens),
        "resumo": resumo,
        "dados": itens,
    }), 200


@api_bp.route('/carteira', methods=['POST'])
def post_carteira():
    """Registra uma compra simulada em BRL na Carteira Virtual."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie um objeto JSON válido com 'moeda' e 'valor_investido'",
        }), 400

    moeda = body.get('moeda', '')
    valor_bruto = body.get('valor_investido')

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

    investimento, erro = criar_investimento(moeda, valor_investido)
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Compra simulada registrada na carteira com sucesso",
        "dados": investimento.to_dict(),
    }), 201


@api_bp.route('/carteira/<int:investimento_id>', methods=['DELETE'])
def delete_carteira(investimento_id):
    """Remove (simula a venda) de um investimento da carteira pelo ID."""
    ok, erro = remover_investimento(investimento_id)
    if not ok:
        return jsonify({"sucesso": False, "mensagem": erro}), _status_por_erro(erro)

    return jsonify({
        "sucesso": True,
        "mensagem": "Investimento removido da carteira com sucesso",
    }), 200
