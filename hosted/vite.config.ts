import {defineConfig,loadEnv} from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({mode})=>{
 const env=loadEnv(mode,process.cwd(),'VITE_');
 const key=process.env.VITE_SUPABASE_PUBLISHABLE_KEY||env.VITE_SUPABASE_PUBLISHABLE_KEY||'';
 let privateKey=key.startsWith('sb_secret_');
 try{privateKey=privateKey||JSON.parse(Buffer.from(key.split('.')[1]||'','base64url').toString()).role==='service_role'}catch{}
 if(privateKey)throw new Error('Refusing to bundle a Supabase private/service-role key. Use a publishable/anon key.');
 return {plugins:[react()],server:{host:'127.0.0.1',strictPort:true},build:{target:'es2022'}};
});
