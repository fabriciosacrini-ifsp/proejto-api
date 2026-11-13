import { useEffect } from 'react'
import { X } from 'lucide-react'

/**
 * Janela Pop-up reutilizável.
 * Fecha ao clicar no X, clicar fora do card ou apertar a tecla ESC.
 */
export default function Modal({ aberto, titulo, subtitulo, icone, onFechar, children }) {
  useEffect(() => {
    if (!aberto) return

    function aoApertarTecla(evento) {
      if (evento.key === 'Escape') {
        onFechar()
      }
    }

    window.addEventListener('keydown', aoApertarTecla)
    return () => window.removeEventListener('keydown', aoApertarTecla)
  }, [aberto, onFechar])

  if (!aberto) return null

  return (
    <div
      className="modal-fundo"
      role="dialog"
      aria-modal="true"
      onClick={(e) => {
        if (e.target === e.currentTarget) onFechar()
      }}
    >
      <div className="modal-card">
        <div className="modal-topo">
          <div className="titulo-com-icone">
            {icone}
            <div>
              <h3>{titulo}</h3>
              {subtitulo && <span className="modal-subtitulo">{subtitulo}</span>}
            </div>
          </div>

          <button
            type="button"
            className="btn-icone"
            onClick={onFechar}
            aria-label="Fechar janela"
            title="Fechar"
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-corpo">{children}</div>
      </div>
    </div>
  )
}
