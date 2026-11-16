import {defineConfig} from 'vitest/config';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],test:{include:['src/test/**/*.test.{ts,tsx}'],environment:'jsdom',setupFiles:['./src/test/setup.ts'],restoreMocks:true,coverage:{provider:'v8',reporter:['text','json-summary','html'],include:['src/**/*.{ts,tsx}'],exclude:['src/vendor/**','src/test/**','src/main.tsx','src/vite-env.d.ts']}}});
