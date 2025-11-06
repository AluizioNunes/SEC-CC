import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Não precisamos do plugin React no Vitest; o Vite já o usa no build.
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/test/setup.ts'],
    include: ['src/__tests__/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['Backend/**', 'Services/**', 'node_modules/**'],
  },
});