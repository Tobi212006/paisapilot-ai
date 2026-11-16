import {createClient} from "@supabase/supabase-js";
import {setAccessToken} from "./api";

const url=(import.meta.env.VITE_SUPABASE_URL||"").trim();
const key=(import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY||"").trim();
export const authConfigurationError=Boolean(url)!==Boolean(key)?"Set both Supabase public project settings.":key.startsWith('sb_secret_')?"A private Supabase key must never be used in the browser.":"";
function client(){
 if(!url||!key||authConfigurationError)return null;
 try{return createClient(url,key,{auth:{persistSession:false,autoRefreshToken:true,detectSessionInUrl:false}})}catch{return null}
}
export const supabase=client();
supabase?.auth.onAuthStateChange((_event,session)=>setAccessToken(session?.access_token||""));
