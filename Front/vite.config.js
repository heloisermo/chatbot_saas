import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true
    },
    proxy: {
      '/auth': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true
      },
      '/documents': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
