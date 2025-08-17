import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 8501,
    host: true,
    allowedHosts: [
      process.env.HOSTNAME ||
        process.env.VITE_DEFAULT_ALLOWED_HOST ||
        'localhost',
    ],
  },
  build: {
    outDir: 'dist',
  },
})
