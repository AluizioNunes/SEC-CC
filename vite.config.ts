import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuração de performance: chunking e otimização de dependências
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  build: {
    target: 'es2020',
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom'],

          antd: ['antd', '@ant-design/icons'],
          motion: ['framer-motion'],
          charts: ['echarts', 'echarts-for-react'],
          utils: ['axios', 'date-fns', 'dayjs'],
        },
      },
    },
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'antd',
      '@ant-design/icons',
      'framer-motion',
      'echarts',
      'echarts-for-react',
      'axios',
      'date-fns',
      'dayjs',
    ],
  },
});