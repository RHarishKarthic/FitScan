import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5175,
  },
  plugins: [react({
    jsxRuntime: 'automatic'
  })],
  define: {
    'process': {
      env: {
        NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development'),
      },
    },
  },
})
