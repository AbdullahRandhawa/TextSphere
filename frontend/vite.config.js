import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks: {
          // Split Firebase SDK into its own chunk
          firebase: ['firebase/app', 'firebase/auth', 'firebase/firestore'],
          // Split React into its own chunk
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
  server: {
    port: 5173,
    watch: {
      // Exclude Firebase credentials JSON and any large/locked files from the watcher.
      // This prevents the EBUSY crash when the credentials file is inside the project root.
      ignored: [
        '**/*firebase-adminsdk*.json',
        '**/*credentials*.json',
        '**/firebase_credentials.json',
      ],
    },
  },
});
