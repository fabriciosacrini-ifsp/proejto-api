import { useState } from 'react'
import {
  AlertTriangle,
  Clock,
  Coins,
  Minus,
  Plus,
  Receipt,
  RefreshCw,
  Trash2,
  TrendingDown,
  TrendingUp,
  Wallet,
} from 'lucide-react'
import IconeMoeda from './IconeMoeda'
import Modal from './Modal'
import {
  formatarCripto,
  formatarDinheiro,
  formatarVariacao,
} from '../utils/formatters'

const MAPA_STATUS = {
  LUCRO: { icone: TrendingUp, classe: 'badge-alta' },
  PREJUIZO: { icone: TrendingDown, classe: 'badge-baixa' },
  EMPATE: { icone: Minus, classe: 'badge-neutra' },
  INDISPONIVEL: { icone: AlertTriangle, classe: 'badge-info' },
}

export default function CarteiraVirtual({
  moedaSelecionada,
  carteira,
  carregando,
  onAtualizarCarteira,
  onAdicionarCompra,
  onRemoverCompra,
}) {
  const [valorCompra, setValorCompra] = useState('250')
  const [enviando, setEnviando] = useState(false)
  const [idRemovendo, setIdRemovendo] = useState(null)
  const [erroForm, setErroForm] = useState('')
  const [modalAberto, setModalAberto] = useState(false)

  const itens = carteira?.dados || []
  const resumo = carteira?.resumo || null

  async function handleNovaCompra(evento) {
    evento.preventDefault()
    setErroForm('')
    setEnviando(true)

    try {
      await onAdicionarCompra(valorCompra)
    } catch (err) {
      setErroForm(err.message)
    } finally {
      setEnviando(false)
    }
  }

  async function handleVender(id) {
    setIdRemovendo(id)
    setErroForm('')

    try {
      await onRemoverCompra(id)
    } catch (err) {
      setErroForm(err.message)
    } finally {
      setIdRemovendo(null)
    }
  }

  const lucroTotal = resumo?.lucro_prejuizo_total || 0
  const IconeResultado =
    lucroTotal > 0 ? TrendingUp : lucroTotal < 0 ? TrendingDown : Minus
  const classeResultado =
    lucroTotal > 0 ? 'texto-alta' : lucroTotal < 0 ? 'texto-baixa' : ''

  return (
    <section className="card">
      <div className="card-topo">
        <div className="titulo-com-icone">
          <Wallet size={18} className="icone-destaque" />
          <h2>Carteira • {moedaSelecionada.nome}</h2>
        </div>

        <div className="acoes-topo">
          <button
            type="button"
            className="btn btn-secundario btn-compacto"
            onClick={() => setModalAberto(true)}
            title="Abrir histórico de compras desta moeda"
          >
            <Receipt size={15} />
            <span>Compras ({itens.length})</span>
          </button>

          <button
            type="button"
            className="btn btn-secundario btn-compacto"
            onClick={() => onAtualizarCarteira(true)}
            disabled={carregando}
            title="Buscar nova cotação na Coinbase e recalcular carteira"
          >
            <RefreshCw size={15} className={carregando ? 'girando' : ''} />
          </button>
        </div>
      </div>

      {/* Compra rápida em Reais */}
      <form className="formulario-linha" onSubmit={handleNovaCompra}>
        <div className="input-com-prefixo">
          <span className="prefixo">R$</span>
          <input
            type="text"
            inputMode="decimal"
            aria-label={`Valor para investir em ${moedaSelecionada.codigo}`}
            placeholder="250"
            value={valorCompra}
            onChange={(e) => setValorCompra(e.target.value)}
          />
        </div>

        <button type="submit" className="btn btn-sucesso btn-compacto" disabled={enviando}>
          {enviando ? (
            <RefreshCw size={15} className="girando" />
          ) : (
            <Plus size={16} />
          )}
          <span>Comprar {moedaSelecionada.codigo}</span>
        </button>
      </form>

      {erroForm && <p className="mensagem-erro">{erroForm}</p>}

      {!resumo ? (
        <div className="estado-vazio-minimal">
          <IconeMoeda codigo={moedaSelecionada.codigo} tamanho={24} />
          <span>Nenhuma compra em {moedaSelecionada.codigo}</span>
        </div>
      ) : (
        <div className="resumo-carteira-quatro">
          <div className="mini-card destaque-cripto">
            <span className="label-icone">
              <Coins size={13} /> Quantidade Total
            </span>
            <strong className="valor-icone">
              <IconeMoeda codigo={moedaSelecionada.codigo} tamanho={18} />
              <span>
                {formatarCripto(resumo.quantidade_total_cripto, moedaSelecionada.codigo)}
              </span>
            </strong>
          </div>

          <div className="mini-card">
            <span className="label-pequena">Investido</span>
            <strong>{formatarDinheiro(resumo.total_investido)}</strong>
          </div>

          <div className="mini-card">
            <span className="label-pequena">Valor Hoje</span>
            <strong>{formatarDinheiro(resumo.total_atual)}</strong>
          </div>

          <div className="mini-card">
            <span className="label-pequena">Resultado</span>
            <strong className={`valor-icone ${classeResultado}`}>
              <IconeResultado size={15} />
              <span>
                {lucroTotal > 0 ? '+' : ''}
                {formatarDinheiro(lucroTotal)} (
                {formatarVariacao(resumo.variacao_total_percentual)})
              </span>
            </strong>
          </div>
        </div>
      )}

      {/* Pop-up com o histórico de compras dessa moeda e opção de vender */}
      <Modal
        aberto={modalAberto}
        titulo={`Minhas Compras • ${moedaSelecionada.nome}`}
        subtitulo={`${itens.length} compra(s) registrada(s)`}
        icone={<IconeMoeda codigo={moedaSelecionada.codigo} tamanho={26} />}
        onFechar={() => setModalAberto(false)}
      >
        {itens.length === 0 ? (
          <div className="estado-vazio-minimal">
            <Wallet size={22} />
            <span>Nenhuma compra registrada em {moedaSelecionada.codigo}</span>
          </div>
        ) : (
          <>
            {resumo && (
              <div className="modal-resumo-topo">
                <div className="modal-resumo-item">
                  <span>Total acumulado</span>
                  <strong>
                    {formatarCripto(
                      resumo.quantidade_total_cripto,
                      moedaSelecionada.codigo
                    )}
                  </strong>
                </div>
                <div className="modal-resumo-item">
                  <span>Total investido</span>
                  <strong>{formatarDinheiro(resumo.total_investido)}</strong>
                </div>
                <div className="modal-resumo-item">
                  <span>Valor hoje</span>
                  <strong>{formatarDinheiro(resumo.total_atual)}</strong>
                </div>
              </div>
            )}

            <div className="modal-lista">
              {itens.map((item) => {
                const statusInfo = MAPA_STATUS[item.status] || MAPA_STATUS.EMPATE
                const IconeStatus = statusInfo.icone
                const removendoEste = idRemovendo === item.id

                return (
                  <div key={item.id} className="modal-compra-card">
                    <div className="modal-item-esq">
                      <IconeMoeda codigo={item.simbolo} tamanho={28} />
                      <div>
                        <div className="modal-item-titulo">
                          {formatarCripto(item.quantidade_cripto, item.simbolo)}
                        </div>
                        <div className="modal-item-data">
                          <Clock size={12} />
                          <span>{item.data_compra}</span>
                          <span>•</span>
                          <span>Pagou {formatarDinheiro(item.preco_na_compra)}/un.</span>
                        </div>
                      </div>
                    </div>

                    <div className="modal-compra-valores">
                      <div>
                        <span className="label-pequena">Investido</span>
                        <strong>{formatarDinheiro(item.valor_investido)}</strong>
                      </div>
                      <div>
                        <span className="label-pequena">Hoje</span>
                        <strong>
                          {item.cotacao_disponivel
                            ? formatarDinheiro(item.valor_atual)
                            : '--'}
                        </strong>
                      </div>
                    </div>

                    <div className="modal-compra-acoes">
                      {item.cotacao_disponivel ? (
                        <span className={`badge badge-icone ${statusInfo.classe}`}>
                          <IconeStatus size={13} />
                          <span>
                            {item.lucro_prejuizo > 0 ? '+' : ''}
                            {formatarDinheiro(item.lucro_prejuizo)} (
                            {formatarVariacao(item.variacao_percentual)})
                          </span>
                        </span>
                      ) : (
                        <span className="badge badge-info">Indisponível</span>
                      )}

                      <button
                        type="button"
                        className="btn btn-perigo btn-pequeno"
                        onClick={() => handleVender(item.id)}
                        disabled={removendoEste}
                        title="Vender investimento"
                      >
                        {removendoEste ? (
                          <RefreshCw size={14} className="girando" />
                        ) : (
                          <Trash2 size={14} />
                        )}
                        <span>Vender</span>
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </>
        )}
      </Modal>
    </section>
  )
}
