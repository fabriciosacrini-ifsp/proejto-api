// Endereço onde a API Flask está rodando localmente
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api'

/**
 * Garante um giro mínimo (350ms) nas setinhas dos botões mesmo quando a resposta é instantânea.
 */
export async function comGiroMinimo(promessa, tempoMs = 350) {
  const [resultado] = await Promise.all([
    promessa,
    new Promise((resolve) => setTimeout(resolve, tempoMs)),
  ])
  return resultado
}

/**
 * Função auxiliar que faz a requisição fetch e já trata erros de conexão ou JSON.
 */
async function requisitar(caminho, opcoes = {}) {
  let resposta

  try {
    resposta = await fetch(`${API_URL}${caminho}`, opcoes)
  } catch {
    throw new Error(
      'Não foi possível conectar à API Flask (porta 5000). Verifique se o backend está ligado.'
    )
  }

  const dados = await resposta.json().catch(() => null)

  if (!resposta.ok) {
    const erro = new Error(dados?.mensagem || 'Erro inesperado na API Flask')
    erro.status = resposta.status
    throw erro
  }

  return dados
}

// 1. Lista as criptomoedas aceitas pelo backend
export function buscarMoedas() {
  return requisitar('/moedas')
}

// 2. Busca a cotação em Reais na Coinbase, grava no SQLite e devolve o termômetro
export function consultarCotacao(moeda) {
  return comGiroMinimo(requisitar(`/cripto/${moeda}`))
}

// 3. Busca apenas o termômetro já salvo no banco para aquela moeda
export async function buscarResumoMoeda(moeda) {
  try {
    const dados = await requisitar(`/cripto/${moeda}/resumo`)
    return dados.termometro
  } catch (erro) {
    if (erro.status === 404) {
      return null
    }
    throw erro
  }
}

// 4. Lista o histórico de cotações salvas no SQLite para aquela moeda
export function buscarHistorico(moeda) {
  return requisitar(`/cripto/historico?moeda=${moeda}`)
}

// 5. Converte um valor em Reais (BRL) para a quantidade de cripto
export function converterValor(moeda, valor) {
  const valorLimpo = encodeURIComponent(String(valor).trim())
  return comGiroMinimo(requisitar(`/converter?moeda=${moeda}&valor=${valorLimpo}`))
}

// 6. Lista os investimentos da Carteira Virtual apenas da moeda escolhida
export function buscarCarteira(moeda, forcarAtualizacao = false) {
  const extra = forcarAtualizacao ? '&atualizar=1' : ''
  const chamada = requisitar(`/carteira?moeda=${moeda}${extra}`)
  return forcarAtualizacao ? comGiroMinimo(chamada) : chamada
}

// 7. Registra uma nova compra simulada em BRL na Carteira Virtual
export function criarInvestimento(moeda, valorInvestido) {
  return comGiroMinimo(
    requisitar('/carteira', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        moeda,
        valor_investido: valorInvestido,
      }),
    })
  )
}

// 8. Atualiza o valor investido de uma compra já salva pelo ID (UPDATE)
export function atualizarInvestimento(id, novoValorInvestido) {
  return comGiroMinimo(
    requisitar(`/carteira/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        valor_investido: novoValorInvestido,
      }),
    })
  )
}

// 9. Remove (simula a venda) de um investimento da carteira pelo ID (DELETE)
export function removerInvestimento(id) {
  return comGiroMinimo(
    requisitar(`/carteira/${id}`, {
      method: 'DELETE',
    })
  )
}
