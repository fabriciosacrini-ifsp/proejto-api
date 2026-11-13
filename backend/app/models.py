from datetime import datetime
from app import db


class PrecoCripto(db.Model):
    """Tabela 1: Guarda o histórico de cotações consultadas na Coinbase."""
    __tablename__ = 'precos_cripto'

    id = db.Column(db.Integer, primary_key=True)
    simbolo = db.Column(db.String(10), nullable=False)               # Ex: 'BTC', 'ETH'
    moeda_base = db.Column(db.String(10), nullable=False, default='BRL')
    preco = db.Column(db.Float, nullable=False)                      # Preço em Reais (R$)
    data_consulta = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "simbolo": self.simbolo,
            "moeda_base": self.moeda_base,
            "preco": round(self.preco, 2),
            "data_consulta": self.data_consulta.strftime("%Y-%m-%d %H:%M:%S")
        }


class Investimento(db.Model):
    """Tabela 2: Guarda as compras simuladas da Carteira Virtual."""
    __tablename__ = 'investimentos'

    id = db.Column(db.Integer, primary_key=True)
    simbolo = db.Column(db.String(10), nullable=False)               # Ex: 'BTC', 'ETH'
    moeda_base = db.Column(db.String(10), nullable=False, default='BRL')
    valor_investido = db.Column(db.Float, nullable=False)            # Quanto investiu em R$
    preco_na_compra = db.Column(db.Float, nullable=False)            # Preço de 1 unidade na hora da compra
    quantidade_cripto = db.Column(db.Float, nullable=False)          # Fração comprada (valor / preco_na_compra)
    data_compra = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "simbolo": self.simbolo,
            "moeda_base": self.moeda_base,
            "valor_investido": round(self.valor_investido, 2),
            "preco_na_compra": round(self.preco_na_compra, 2),
            "quantidade_cripto": round(self.quantidade_cripto, 8),
            "data_compra": self.data_compra.strftime("%Y-%m-%d %H:%M:%S")
        }
