/**
 * Funções simples para formatar Reais (R$), frações de cripto e porcentagens.
 */

export function formatarDinheiro(valor) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) {
    return '--'
  }

  // Evita exibir "-R$ 0,00" por arredondamento
  const numeroLimpo = Math.abs(Number(valor)) < 0.005 ? 0 : Number(valor)

  return numeroLimpo.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

export function formatarCripto(quantidade, simbolo = '') {
  if (quantidade === null || quantidade === undefined || Number.isNaN(quantidade)) {
    return '--'
  }

  const numeroFormatado = Number(quantidade).toLocaleString('pt-BR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 8,
  })

  return simbolo ? `${numeroFormatado} ${simbolo}` : numeroFormatado
}

export function formatarVariacao(percentual) {
  if (percentual === null || percentual === undefined || Number.isNaN(percentual)) {
    return '--'
  }

  // Evita exibir "-0,00%"
  const valorLimpo = Math.abs(Number(percentual)) < 0.005 ? 0 : Number(percentual)
  const sinal = valorLimpo > 0 ? '+' : ''
  const numero = valorLimpo.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return `${sinal}${numero}%`
}
