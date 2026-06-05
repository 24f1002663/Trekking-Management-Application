import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// The Flask API runs on :8080. In dev, Vite serves the SPA on :5173 and
// proxies all API + uploaded-file requests to Flask. In prod, `npm run build`
// emits to ../frontend/dist which Flask serves directly.
export default defineConfig({
  plugins: [vue()],
  base: '/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8080',
      '/admin': 'http://localhost:8080',
      '/user': 'http://localhost:8080',
      '/staff': 'http://localhost:8080',
      '/static': 'http://localhost:8080',
    },
  },
})
