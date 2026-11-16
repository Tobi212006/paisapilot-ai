import {useEffect,useState} from "react";
import {api,isSignedIn} from "./api";
import {supabase,authConfigurationError} from "./authClient";
import type {Connections} from "./MoneyTools";

export function AccountPanel({onChange}:{onChange:()=>void}){
 const[connections,setConnections]=useState<Connections|null>(null),[error,setError]=useState(""),[message,setMessage]=useState("");
 const[email,setEmail]=useState(""),[password,setPassword]=useState(""),[signedIn,setSignedIn]=useState(isSignedIn),[busy,setBusy]=useState(false),[confirmation,setConfirmation]=useState("");
 useEffect(()=>{let current=true;api<Connections>("/api/connections").then(c=>{if(current)setConnections(c)}).catch(e=>{if(current)setError(e.message)});return()=>{current=false}},[]);
 useEffect(()=>{const update=()=>setSignedIn(isSignedIn());window.addEventListener('paisapilot-session',update);return()=>window.removeEventListener('paisapilot-session',update)},[]);
 async function sign(mode:"signup"|"signin"){
  if(!supabase)return;setBusy(true);setError("");setMessage("");
  try{
   const credentials={email:email.trim(),password};
   const result=mode==='signup'?await supabase.auth.signUp(credentials):await supabase.auth.signInWithPassword(credentials);
   if(result.error)throw result.error;
   setPassword("");setMessage(result.data.session?"Signed in. Your private workspace is ready.":"Check your email to confirm your account, then sign in.");onChange();
  }catch(e){setError((e as Error).message||"Sign-in failed. Please try again.")}finally{setBusy(false)}
 }
 async function signOut(){if(!supabase)return;setBusy(true);setError("");try{const{error}=await supabase.auth.signOut({scope:'local'});if(error)throw error;setMessage("Signed out on this device.");onChange()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function exportData(){setBusy(true);setError("");try{const data=await api("/api/records/export");const objectUrl=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));const link=document.createElement('a');link.href=objectUrl;link.download='paisapilot-records.json';link.click();setTimeout(()=>URL.revokeObjectURL(objectUrl),1000);setMessage("Your JSON export is ready.")}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 async function clear(){setBusy(true);setError("");try{await api("/api/records/clear",{method:"POST",body:JSON.stringify({confirmation})});setConfirmation("");setMessage("Workspace records deleted. Your sign-in account is retained.");onChange()}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 const privateMode=connections?.workspace_mode==='private',canAccess=connections?.workspace_mode==='demo'||(privateMode&&signedIn);
 return <><section className="panel tool-panel"><span className="eyebrow">YOUR WORKSPACE & CONNECTIONS</span><h3>{privateMode?"A space for your own records.":"Explore in the local demo workspace."}</h3><p className="muted">{privateMode?"Sign in to access your records. Sessions refresh automatically while this page is open. Reloading requires sign-in again.":"Account setup is pending. This is a shared demo on this computer; use sample records only."}</p>
 {privateMode&&!signedIn&&supabase&&<form onSubmit={e=>{e.preventDefault();sign('signin')}}><label>Email<input type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)} disabled={busy}/></label><label>Password<input type="password" autoComplete="current-password" minLength={1} required value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/></label><div className="inline-actions"><button disabled={busy} className="primary-btn">Sign in</button><button disabled={busy||!email.includes('@')||password.length<8} className="pill-button outline" type="button" onClick={()=>sign('signup')}>Create account</button></div></form>}
 {signedIn&&<button className="pill-button outline" disabled={busy} onClick={signOut}>Sign out</button>}
 {(authConfigurationError||(privateMode&&!supabase))&&<p className="tool-error">{authConfigurationError||"Sign-in configuration is incomplete. Set the frontend Supabase public settings."}</p>}
 {connections?.workspace_mode==='configuration_error'&&<p className="tool-error">The server requires sign-in but its account configuration is incomplete. Private data remains unavailable.</p>}
 {connections&&<div className="connection-list">{[["Mutual fund NAV","Public API · verify in Market Lab"],["Currency rates","Public API · verify in Currency"],["Private sign-in",connections.supabase.configured?"Configured · sign-in required":"Setup needed"],["Upstox stock quotes",connections.upstox.configured?"Key configured · verify with a quote":"Token needed"],["Pip learning AI",connections.assistant.configured?"Key configured · verify with a topic":"Key needed"]].map(([label,status])=><div key={label}><span>{label}</span><b>{status}</b></div>)}</div>}
 </section><section className="panel tool-panel"><h3>Your data, your choice.</h3><p className="muted">Export your workspace as JSON. Deletion permanently removes its transactions, goals, contributions, category limits, invoices and import history.</p><button className="pill-button outline" disabled={busy||!canAccess} onClick={exportData}>Export records</button><label>Type DELETE MY RECORDS to remove workspace records<input value={confirmation} disabled={busy||!canAccess} onChange={e=>setConfirmation(e.target.value)}/></label><button className="danger-button" disabled={busy||!canAccess||confirmation!=="DELETE MY RECORDS"} onClick={clear}>Delete workspace records</button></section>
 {error&&<p role="alert" className="tool-error">{error}</p>}{message&&<p role="status" className="tool-success">{message}</p>}</>
}
