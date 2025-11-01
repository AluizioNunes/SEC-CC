import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configuração de performance: chunking e otimização de dependências
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    target: 'es2020',
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined;
          if (id.includes('react')) return 'react';
          if (id.includes('antd') || id.includes('@ant-design/icons')) return 'antd';
          if (id.includes('framer-motion')) return 'motion';
          if (id.includes('echarts') || id.includes('echarts-for-react')) return 'charts';
          if (id.includes('axios') || id.includes('date-fns') || id.includes('dayjs')) return 'utils';
          return undefined;
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