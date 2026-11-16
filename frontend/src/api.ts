const BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
let accessToken = "";
let sessionVersion = 0;
export function setAccessToken(token:string){if(token===accessToken)return;accessToken=token;sessionVersion++;window.dispatchEvent(new Event('paisapilot-session'));}
export function isSignedIn(){return Boolean(accessToken)}
export async function api<T>(path: string, options?: RequestInit): Promise<T> {
 if(!path.startsWith('/api/'))throw new Error('Invalid API path.');
 const version=sessionVersion;
 let response:Response;
 try{response=await fetch(`${BASE}${path}`, { ...options, signal:options?.signal||AbortSignal.timeout(35000), headers: { "Content-Type": "application/json", ...(accessToken?{Authorization:`Bearer ${accessToken}`} : {}), ...(options?.headers || {}) } })}catch(e){if(e instanceof DOMException&&(e.name==='TimeoutError'||e.name==='AbortError'))throw new Error('The request timed out. Please try again.');throw new Error('Could not reach the server. Check your connection and try again.');}
 if(version!==sessionVersion)throw new Error('Session changed. Please reload this view.');
 if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(typeof body.detail==='string'?body.detail:response.status===422?'Check your inputs and try again.':`Request failed (${response.status})`); }
 let result;try{result=await response.json()}catch{throw new Error('The server returned an invalid response. Please try again.');}
 if(version!==sessionVersion)throw new Error('Session changed. Please reload this view.');
 return result as T;
}
