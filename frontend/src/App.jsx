import { useEffect, useState } from 'react'
import { AlertCircle, Coins, Moon, RefreshCw, Sun } from 'lucide-react'
import {
  buscarCarteira,
  buscarHistorico,
  buscarMoedas,
  buscarResumoMoeda,
  consultarCotacao,
  criarInvestimento,
  removerInvestimento,
} from './services/api'
import IconeMoeda from './components/IconeMoeda'
import TermometroCripto from './components/TermometroCripto'
import ConversorCripto from './components/ConversorCripto'
import CarteiraVirtual from './components/CarteiraVirtual'

const MOEDAS_PADRAO = [
  { codigo: 'BTC', chave: 'btc', nome: 'Bitcoin' },
  { codigo: 'ETH', chave: 'eth', nome: 'Ethereum' },
  { codigo: 'LINK', chave: 'link', nome: 'Chainlink' },
  { codigo: 'SOL', chave: 'sol', nome: 'Solana' },
]

export default function App() {
  const [tema, setTema] = useState(() => localStorage.getItem('tema') || 'dark')
  const [moedas, setMoedas] = useState(MOEDAS_PADRAO)
  const [moedaChave, setMoedaChave] = useState('btc')

  const [termometro, setTermometro] = useState(null)
  const [historico, setHistorico] = useState([])
  const [carteira, setCarteira] = useState({
    total_itens: 0,
    resumo: null,
    dados: [],
  })

  const [erroGeral, setErroGeral] = useState('')
  const [carregandoCotacao, setCarregandoCotacao] = useState(false)
  const [carregandoCarteira, setCarregandoCarteira] = useState(false)

  const moedaSelecionada =
    moedas.find((m) => m.chave === moedaChave) || MOEDAS_PADRAO[0]

  // Aplica o tema claro/escuro na página
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', tema)
    localStorage.setItem('tema', tema)
  }, [tema])

  // Carrega a lista de moedas suportadas ao iniciar
  useEffect(() => {
    buscarMoedas()
      .then((dadosMoedas) => {
        if (dadosMoedas.criptomoedas?.length) {
          setMoedas(dadosMoedas.criptomoedas)
        }
      })
      .catch((err) => setErroGeral(err.message))
  }, [])

  // Sempre que trocar de cripto (BTC, ETH, LINK, SOL), carrega os dados daquela moeda
  useEffect(() => {
    carregarTelaMoeda()
  }, [moedaChave])

  async function carregarTelaMoeda() {
    try {
      const [resumo, hist, dadosCarteira] = await Promise.all([
        buscarResumoMoeda(moedaChave),
        buscarHistorico(moedaChave),
        buscarCarteira(moedaChave),
      ])
      setTermometro(resumo)
      setHistorico(hist.dados || [])
      setCarteira(dadosCarteira)
      setErroGeral('')
    } catch (err) {
      setErroGeral(err.message)
    }
  }

  async function carregarCarteira(forcarAtualizacao = false) {
    setCarregandoCarteira(true)
    try {
      const dados = await buscarCarteira(moedaChave, forcarAtualizacao)
      setCarteira(dados)
      setErroGeral('')
    } catch (err) {
      setErroGeral(err.message)
    } finally {
      setCarregandoCarteira(false)
    }
  }

  async function handleConsultarCoinbase() {
    setCarregandoCotacao(true)
    setErroGeral('')

    try {
      const resposta = await consultarCotacao(moedaChave)
      setTermometro(resposta.termometro)

      const hist = await buscarHistorico(moedaChave)
      setHistorico(hist.dados || [])
      await carregarCarteira(false)
    } catch (err) {
      setErroGeral(err.message)
    } finally {
      setCarregandoCotacao(false)
    }
  }

  async function handleAdicionarCompra(valor) {
    await criarInvestimento(moedaChave, valor)
    await carregarCarteira(false)
  }

  async function handleRemoverCompra(id) {
    await removerInvestimento(id)
    await carregarCarteira(false)
  }

  return (
    <div className="pagina" data-moeda={moedaChave}>
      <header className="cabecalho">
        <div className="titulo-com-icone">
          <Coins size={24} className="icone-destaque" />
          <h1>CriptoMonitor</h1>
        </div>

        <div className="cabecalho-acoes">
          <button
            type="button"
            className="btn-icone"
            onClick={() => setTema(tema === 'dark' ? 'light' : 'dark')}
            aria-label={tema === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}
            title={tema === 'dark' ? 'Tema Claro' : 'Tema Escuro'}
          >
            {tema === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      {erroGeral && (
        <div className="banner-erro">
          <div className="titulo-com-icone">
            <AlertCircle size={16} />
            <span>{erroGeral}</span>
          </div>
          <button
            type="button"
            className="btn btn-secundario btn-pequeno"
            onClick={carregarTelaMoeda}
          >
            <RefreshCw size={14} />
            <span>Reconectar</span>
          </button>
        </div>
      )}

      <section className="barra-filtros">
        <div className="grupo-botoes" role="group" aria-label="Escolher criptomoeda">
          {moedas.map((moeda) => (
            <button
              key={moeda.chave}
              type="button"
              className={`pill ${moedaChave === moeda.chave ? 'ativo' : ''}`}
              onClick={() => setMoedaChave(moeda.chave)}
            >
              <IconeMoeda codigo={moeda.codigo} tamanho={20} />
              <strong>{moeda.codigo}</strong>
              <span className="pill-nome">{moeda.nome}</span>
            </button>
          ))}
        </div>
      </section>

      <main className="conteudo">
        <div className="grade-superior">
          <TermometroCripto
            moedaSelecionada={moedaSelecionada}
            termometro={termometro}
            historico={historico}
            carregando={carregandoCotacao}
            onAtualizarCotacao={handleConsultarCoinbase}
          />

          <ConversorCripto moedaSelecionada={moedaSelecionada} />
        </div>

        <CarteiraVirtual
          moedaSelecionada={moedaSelecionada}
          carteira={carteira}
          carregando={carregandoCarteira}
          onAtualizarCarteira={carregarCarteira}
          onAdicionarCompra={handleAdicionarCompra}
          onRemoverCompra={handleRemoverCompra}
        />
      </main>
    </div>
  )
}
