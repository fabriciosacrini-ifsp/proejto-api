from datetime import datetime
from app import db


class Moeda(db.Model):
    """
    Tabela 1 (moedas): Cadastra as criptomoedas monitoradas pelo sistema.
    Relacionamentos (1:N):
    - Uma Moeda pode ter várias cotações no histórico (PrecoCripto).
    - Uma Moeda pode estar em várias compras simuladas (Investimento).
    """
    __tablename__ = 'moedas'

    id = db.Column(db.Integer, primary_key=True)
    simbolo = db.Column(db.String(10), unique=True, nullable=False)  # Ex: 'BTC', 'ETH'
    nome = db.Column(db.String(50), nullable=False)                  # Ex: 'Bitcoin', 'Ethereum'

    # Relacionamentos 1 para N (uma moeda -> vários preços e vários investimentos)
    cotacoes = db.relationship(
        'PrecoCripto',
        back_populates='moeda',
        cascade='all, delete-orphan',
        lazy=True,
    )
    investimentos = db.relationship(
        'Investimento',
        back_populates='moeda',
        cascade='all, delete-orphan',
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.simbolo.upper(),
            "chave": self.simbolo.lower(),
            "nome": self.nome,
        }


class Carteira(db.Model):
    """
    Tabela 2 (carteiras): Cadastra as carteiras/perfis de investidores.
    Relacionamento (1:N):
    - Uma Carteira pode guardar várias compras simuladas (Investimento).
    """
    __tablename__ = 'carteiras'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)                  # Ex: 'Carteira Principal'
    titular = db.Column(db.String(60), nullable=False)               # Ex: 'Fabricio'
    perfil = db.Column(db.String(30), nullable=False, default='Moderado')
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # Relacionamento 1 para N (uma carteira -> vários investimentos)
    investimentos = db.relationship(
        'Investimento',
        back_populates='carteira',
        cascade='all, delete-orphan',
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "titular": self.titular,
            "perfil": self.perfil,
            "total_compras": len(self.investimentos),
            "data_criacao": self.data_criacao.strftime("%Y-%m-%d %H:%M:%S"),
        }


class PrecoCripto(db.Model):
    """
    Tabela 3 (precos_cripto): Guarda o histórico de cotações consultadas na Coinbase.
    Relacionamento (N:1):
    - Pertence a uma Moeda através da chave estrangeira 'moeda_id'.
    """
    __tablename__ = 'precos_cripto'

    id = db.Column(db.Integer, primary_key=True)
    moeda_id = db.Column(db.Integer, db.ForeignKey('moedas.id'), nullable=False)
    simbolo = db.Column(db.String(10), nullable=False)               # Ex: 'BTC', 'ETH'
    moeda_base = db.Column(db.String(10), nullable=False, default='BRL')
    preco = db.Column(db.Float, nullable=False)                      # Preço em Reais (R$)
    data_consulta = db.Column(db.DateTime, default=datetime.now)

    # Relacionamento N para 1 com a tabela Moeda
    moeda = db.relationship('Moeda', back_populates='cotacoes')

    def to_dict(self):
        return {
            "id": self.id,
            "moeda_id": self.moeda_id,
            "simbolo": self.simbolo,
            "nome_moeda": self.moeda.nome if self.moeda else self.simbolo,
            "moeda_base": self.moeda_base,
            "preco": round(self.preco, 2),
            "data_consulta": self.data_consulta.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Investimento(db.Model):
    """
    Tabela 4 (investimentos): Guarda as compras simuladas da Carteira Virtual.
    Relacionamentos (N:1):
    - Pertence a uma Carteira ('carteira_id' -> carteiras.id).
    - Pertence a uma Moeda ('moeda_id' -> moedas.id).
    """
    __tablename__ = 'investimentos'

    id = db.Column(db.Integer, primary_key=True)
    carteira_id = db.Column(db.Integer, db.ForeignKey('carteiras.id'), nullable=False, default=1)
    moeda_id = db.Column(db.Integer, db.ForeignKey('moedas.id'), nullable=False)
    simbolo = db.Column(db.String(10), nullable=False)               # Ex: 'BTC', 'ETH'
    moeda_base = db.Column(db.String(10), nullable=False, default='BRL')
    valor_investido = db.Column(db.Float, nullable=False)            # Quanto investiu em R$
    preco_na_compra = db.Column(db.Float, nullable=False)            # Preço de 1 unidade na hora da compra
    quantidade_cripto = db.Column(db.Float, nullable=False)          # Fração comprada (valor / preco_na_compra)
    data_compra = db.Column(db.DateTime, default=datetime.now)

    # Relacionamentos N para 1 com Carteira e Moeda
    carteira = db.relationship('Carteira', back_populates='investimentos')
    moeda = db.relationship('Moeda', back_populates='investimentos')

    def to_dict(self):
        return {
            "id": self.id,
            "carteira_id": self.carteira_id,
            "nome_carteira": self.carteira.nome if self.carteira else "Carteira Principal",
            "moeda_id": self.moeda_id,
            "simbolo": self.simbolo,
            "nome_moeda": self.moeda.nome if self.moeda else self.simbolo,
            "moeda_base": self.moeda_base,
            "valor_investido": round(self.valor_investido, 2),
            "preco_na_compra": round(self.preco_na_compra, 2),
            "quantidade_cripto": round(self.quantidade_cripto, 8),
            "data_compra": self.data_compra.strftime("%Y-%m-%d %H:%M:%S"),
        }
