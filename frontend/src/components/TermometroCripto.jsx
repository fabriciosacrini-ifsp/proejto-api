import { useState } from 'react'
import {
  ArrowDown,
  ArrowUp,
  BarChart3,
  Clock,
  History,
  Minus,
  RefreshCw,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'
import IconeMoeda from './IconeMoeda'
import Modal from './Modal'
import { formatarDinheiro, formatarVariacao } from '../utils/formatters'

const MAPA_TENDENCIA = {
  SUBIU: { icone: TrendingUp, classe: 'badge-alta' },
  CAIU: { icone: TrendingDown, classe: 'badge-baixa' },
  MANTEVE: { icone: Minus, classe: 'badge-neutra' },
  PRIMEIRA_CONSULTA: { icone: Sparkles, classe: 'badge-info' },
}

export default function TermometroCripto({
  moedaSelecionada,
  termometro,
  historico,
  carregando,
  onAtualizarCotacao,
}) {
  const [modalAberto, setModalAberto] = useState(false)

  const info = termometro
    ? MAPA_TENDENCIA[termometro.tendencia] || MAPA_TENDENCIA.MANTEVE
    : null
  const IconeTendencia = info?.icone

  return (
    <section className="card">
      <div className="card-topo">
        <div className="titulo-com-icone">
          <IconeMoeda codigo={moedaSelecionada.codigo} tamanho={24} />
          <h2>{moedaSelecionada.nome}</h2>
        </div>

        <div className="acoes-topo">
          <button
            type="button"
            className="btn btn-secundario btn-compacto"
            onClick={() => setModalAberto(true)}
            title="Abrir histórico de cotações"
          >
            <History size={15} />
            <span>{termometro ? termometro.total_consultas : 0}</span>
          </button>

          <button
            type="button"
            className="btn btn-primario btn-compacto"
            onClick={onAtualizarCotacao}
            disabled={carregando}
            title="Buscar cotação atual na Coinbase"
          >
            <RefreshCw size={15} className={carregando ? 'girando' : ''} />
            <span>Atualizar</span>
          </button>
        </div>
      </div>

      {!termometro ? (
        <div className="estado-vazio-minimal">
          <RefreshCw size={22} className={carregando ? 'girando' : ''} />
          <span>Sem cotações salvas para {moedaSelecionada.codigo}</span>
        </div>
      ) : (
        <>
          <div className="preco-destaque-box">
            <div className="preco-grande">{formatarDinheiro(termometro.preco_atual)}</div>

            <div className="tendencia-coluna">
              <span className={`badge badge-icone ${info.classe}`}>
                <IconeTendencia size={14} />
                <span>
                  {termometro.tendencia === 'PRIMEIRA_CONSULTA'
                    ? '1ª consulta'
                    : formatarVariacao(termometro.variacao_percentual)}
                </span>
              </span>

              {termometro.preco_anterior !== null && (
                <span className="diferenca-texto">
                  {termometro.diferenca > 0 ? '+' : ''}
                  {formatarDinheiro(termometro.diferenca)}
                </span>
              )}
            </div>
          </div>

          <div className="grade-estatisticas">
            <div className="mini-card">
              <span className="label-icone">
                <Clock size={13} /> Anterior
              </span>
              <strong>
                {termometro.preco_anterior !== null
                  ? formatarDinheiro(termometro.preco_anterior)
                  : '--'}
              </strong>
            </div>

            <div className="mini-card">
              <span className="label-icone">
                <ArrowUp size={13} /> Máxima
              </span>
              <strong>{formatarDinheiro(termometro.maior_preco)}</strong>
            </div>

            <div className="mini-card">
              <span className="label-icone">
                <ArrowDown size={13} /> Mínima
              </span>
              <strong>{formatarDinheiro(termometro.menor_preco)}</strong>
            </div>

            <div className="mini-card">
              <span className="label-icone">
                <BarChart3 size={13} /> Média
              </span>
              <strong>{formatarDinheiro(termometro.media_preco)}</strong>
            </div>
          </div>
        </>
      )}

      {/* Pop-up com o histórico de cotações dessa moeda */}
      <Modal
        aberto={modalAberto}
        titulo={`Histórico de Cotações • ${moedaSelecionada.nome}`}
        subtitulo={`${historico.length} registro(s) salvo(s) no SQLite`}
        icone={<IconeMoeda codigo={moedaSelecionada.codigo} tamanho={26} />}
        onFechar={() => setModalAberto(false)}
      >
        {historico.length === 0 ? (
          <div className="estado-vazio-minimal">
            <History size={22} />
            <span>Nenhuma consulta registrada para {moedaSelecionada.codigo}</span>
          </div>
        ) : (
          <>
            {termometro && (
              <div className="modal-resumo-topo">
                <div className="modal-resumo-item">
                  <span>Última</span>
                  <strong>{formatarDinheiro(termometro.preco_atual)}</strong>
                </div>
                <div className="modal-resumo-item">
                  <span>Máxima</span>
                  <strong>{formatarDinheiro(termometro.maior_preco)}</strong>
                </div>
                <div className="modal-resumo-item">
                  <span>Mínima</span>
                  <strong>{formatarDinheiro(termometro.menor_preco)}</strong>
                </div>
              </div>
            )}

            <div className="modal-lista">
              {historico.map((item, indice) => {
                const anterior = historico[indice + 1]
                const diff = anterior ? item.preco - anterior.preco : 0

                return (
                  <div key={item.id} className="modal-item-linha">
                    <div className="modal-item-esq">
                      <span className="indice-pill">#{historico.length - indice}</span>
                      <div>
                        <div className="modal-item-titulo">{item.simbolo}</div>
                        <div className="modal-item-data">
                          <Clock size={12} />
                          <span>{item.data_consulta}</span>
                        </div>
                      </div>
                    </div>

                    <div className="modal-item-dir">
                      <strong className="modal-preco">
                        {formatarDinheiro(item.preco)}
                      </strong>
                      {anterior && (
                        <span
                          className={`badge ${
                            diff > 0
                              ? 'badge-alta'
                              : diff < 0
                              ? 'badge-baixa'
                              : 'badge-neutra'
                          }`}
                        >
                          {diff > 0 ? (
                            <TrendingUp size={12} />
                          ) : diff < 0 ? (
                            <TrendingDown size={12} />
                          ) : (
                            <Minus size={12} />
                          )}
                          <span>
                            {diff > 0 ? '+' : ''}
                            {formatarDinheiro(diff)}
                          </span>
                        </span>
                      )}
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
