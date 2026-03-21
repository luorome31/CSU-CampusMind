import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isPlayground = env.VITE_PLAYGROUND === 'true'

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: {
      rollupOptions: {
        input: isPlayground
          ? path.resolve(__dirname, 'playground.html')
          : path.resolve(__dirname, 'index.html'),
      },
    },
    preview: {
      open: isPlayground ? '/playground.html' : '/index.html',
    },
  }
})
