import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// For Docker: use 'http://api:8000', for local: use 'http://localhost:8000'
const API_URL = process.env.API_URL || 'http://api:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: API_URL,
        changeOrigin: true,
        secure: false
      }
    }
  }
})
