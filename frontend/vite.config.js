import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuração simples do Vite para rodar o React na porta 5173
export default defineConfig({
  plugins: [react()],
})
