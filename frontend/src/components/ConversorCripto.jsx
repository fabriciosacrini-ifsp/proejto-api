import { useEffect, useState } from 'react'
import { ArrowRightLeft, Coins, RefreshCw } from 'lucide-react'
import IconeMoeda from './IconeMoeda'
import { converterValor } from '../services/api'
import { formatarCripto, formatarDinheiro } from '../utils/formatters'

export default function ConversorCripto({ moedaSelecionada }) {
  const [valorInput, setValorInput] = useState('100')
  const [resultado, setResultado] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState('')

  // Limpa o resultado anterior quando o usuário troca de criptomoeda
  useEffect(() => {
    setResultado(null)
    setErro('')
  }, [moedaSelecionada.chave])

  async function handleConverter(evento) {
    evento.preventDefault()
    setErro('')
    setCarregando(true)

    try {
      const resposta = await converterValor(moedaSelecionada.chave, valorInput)
      setResultado(resposta.dados)
    } catch (err) {
      setResultado(null)
      setErro(err.message)
    } finally {
      setCarregando(false)
    }
  }

  return (
    <section className="card">
      <div className="card-topo">
        <div className="titulo-com-icone">
          <ArrowRightLeft size={18} className="icone-destaque" />
          <h2>Conversor</h2>
        </div>
      </div>

      <form className="formulario-linha" onSubmit={handleConverter}>
        <div className="input-com-prefixo">
          <span className="prefixo">R$</span>
          <input
            type="text"
            inputMode="decimal"
            aria-label="Valor em Reais"
            placeholder="100"
            value={valorInput}
            onChange={(e) => setValorInput(e.target.value)}
          />
        </div>

        <button type="submit" className="btn btn-primario btn-compacto" disabled={carregando}>
          <RefreshCw size={15} className={carregando ? 'girando' : ''} />
          <span>Converter</span>
        </button>
      </form>

      {erro && <p className="mensagem-erro">{erro}</p>}

      {!resultado && !erro && (
        <div className="estado-vazio-minimal">
          <IconeMoeda codigo={moedaSelecionada.codigo} tamanho={24} />
          <span>Converta Reais para {moedaSelecionada.codigo}</span>
        </div>
      )}

      {resultado && (
        <div className="resultado-conversao">
          <div className="valor-cripto-linha">
            <IconeMoeda codigo={resultado.moeda} tamanho={24} />
            <div className="valor-cripto-destaque">
              {formatarCripto(resultado.quantidade_cripto, resultado.moeda)}
            </div>
          </div>

          <div className="chips-conversao">
            <span className="chip">
              1 {resultado.moeda} = {formatarDinheiro(resultado.preco_unitario)}
            </span>

            {resultado.satoshis !== undefined && (
              <span className="chip chip-info">
                <Coins size={13} />
                <span>{resultado.satoshis.toLocaleString('pt-BR')} sats</span>
              </span>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
