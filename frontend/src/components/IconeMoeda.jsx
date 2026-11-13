/**
 * Ícones em SVG para cada criptomoeda (BTC, ETH, LINK, SOL).
 * Ficam todos em um único arquivo simples, sem precisar de imagens externas.
 */
export default function IconeMoeda({ codigo, tamanho = 20 }) {
  const sigla = String(codigo || '').toUpperCase()

  if (sigla === 'BTC') {
    return (
      <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <circle cx="16" cy="16" r="16" fill="#F7931A" />
        <path
          d="M21.2 14.1c.3-2-1.2-3.1-3.3-3.8l.7-2.7-1.7-.4-.7 2.6c-.4-.1-.9-.2-1.3-.3l.7-2.6-1.7-.4-.7 2.7c-.3-.1-.7-.2-1-.3l-2.3-.6-.4 1.8s1.2.3 1.2.3c.7.2.8.6.8 1l-.8 3.2c.1 0 .2.1.3.1l-.3-.1-1.1 4.5c-.1.2-.3.5-.8.4 0 0-1.2-.3-1.2-.3l-.8 1.9 2.2.5c.4.1.8.2 1.2.3l-.7 2.8 1.7.4.7-2.7c.5.1.9.2 1.3.3l-.7 2.7 1.7.4.7-2.8c2.9.5 5 .3 5.9-2.3.7-2.1 0-3.3-1.5-4.1 1.1-.2 1.9-1 2.1-2.5zm-3.8 5.3c-.5 2.1-4 1-5.1.7l.9-3.7c1.1.3 4.7.8 4.2 3zm.5-5.4c-.5 1.9-3.4.9-4.3.7l.8-3.3c.9.2 4 .7 3.5 2.6z"
          fill="#FFFFFF"
        />
      </svg>
    )
  }

  if (sigla === 'ETH') {
    return (
      <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <circle cx="16" cy="16" r="16" fill="#627EEA" />
        <path d="M16 6v7.4l6.2 2.8L16 6z" fill="#FFFFFF" fillOpacity="0.7" />
        <path d="M16 6L9.8 16.2 16 13.4V6z" fill="#FFFFFF" />
        <path d="M16 21v5l6.2-8.6L16 21z" fill="#FFFFFF" fillOpacity="0.7" />
        <path d="M16 26v-5l-6.2-3.6L16 26z" fill="#FFFFFF" />
        <path d="M16 19.8l6.2-3.6L16 13.4v6.4z" fill="#FFFFFF" fillOpacity="0.45" />
        <path d="M9.8 16.2l6.2 3.6v-6.4l-6.2 2.8z" fill="#FFFFFF" fillOpacity="0.8" />
      </svg>
    )
  }

  if (sigla === 'LINK') {
    return (
      <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <circle cx="16" cy="16" r="16" fill="#2A5ADA" />
        <path
          d="M16 7l-1.8 1-6 3.5L6.4 12.5v7l1.8 1 6 3.5 1.8 1 1.8-1 6-3.5 1.8-1v-7l-1.8-1-6-3.5L16 7zm4.4 11.5L16 21l-4.4-2.5v-5L16 11l4.4 2.5v5z"
          fill="#FFFFFF"
        />
      </svg>
    )
  }

  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <circle cx="16" cy="16" r="16" fill="#141928" />
      <path d="M9.5 20.2c.2-.2.5-.3.8-.3h13.4c.6 0 .9.7.5 1.1l-2.2 2.2c-.2.2-.5.3-.8.3H7.8c-.6 0-.9-.7-.5-1.1l2.2-2.2z" fill="#14F195" />
      <path d="M9.5 8.8c.2-.2.5-.3.8-.3h13.4c.6 0 .9.7.5 1.1L22 11.8c-.2.2-.5.3-.8.3H7.8c-.6 0-.9-.7-.5-1.1l2.2-2.2z" fill="#9945FF" />
      <path d="M22.5 14.4c-.2-.2-.5-.3-.8-.3H8.3c-.6 0-.9.7-.5 1.1l2.2 2.2c.2.2.5.3.8.3h13.4c.6 0 .9-.7.5-1.1l-2.2-2.2z" fill="#00C2FF" />
    </svg>
  )
}
