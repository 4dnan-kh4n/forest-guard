import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_');
  const landingOnly = process.env.VERCEL === '1' || env.VITE_FORESTGUARD_LANDING_ONLY === 'true';
  return {
    define: { __FORESTGUARD_LANDING_ONLY__: JSON.stringify(landingOnly) },
    server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  };
});
