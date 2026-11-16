import {useEffect,useRef,useState,type RefObject} from "react";
import {PanelLeftClose} from "lucide-react";
import type {LucideIcon} from "lucide-react";
import {PilotMark} from "./Brand";

export function useSidebar(){
 const[mobile,setMobile]=useState(()=>window.matchMedia('(max-width:760px)').matches);
 const[open,setOpen]=useState(()=>{if(window.matchMedia('(max-width:760px)').matches)return false;try{return localStorage.getItem('paisapilot-sidebar')!=='closed'}catch{return true}});
 const triggerRef=useRef<HTMLButtonElement>(null);
 useEffect(()=>{const media=window.matchMedia('(max-width:760px)');const update=()=>{setMobile(media.matches);if(media.matches)setOpen(false)};media.addEventListener('change',update);return()=>media.removeEventListener('change',update)},[]);
 useEffect(()=>{if(!mobile){try{localStorage.setItem('paisapilot-sidebar',open?'open':'closed')}catch{}}},[open,mobile]);
 return{open,setOpen,mobile,triggerRef};
}

type Props={page:string;items:readonly(readonly[string,LucideIcon])[];onChoose:(page:string)=>void;onHome?:()=>void;privateMode:boolean;mobile:boolean;onClose:()=>void;triggerRef:RefObject<HTMLButtonElement>};
export function Sidebar({page,items,onChoose,onHome,privateMode,mobile,onClose,triggerRef}:Props){
 const asideRef=useRef<HTMLElement>(null),closeRef=useRef<HTMLButtonElement>(null);
 useEffect(()=>{
  if(!mobile)return;
  closeRef.current?.focus();
  const main=document.getElementById('workspace-main');main?.setAttribute('inert','');
  const oldOverflow=document.body.style.overflow;document.body.style.overflow='hidden';
  return()=>{main?.removeAttribute('inert');document.body.style.overflow=oldOverflow;triggerRef.current?.focus()};
 },[mobile,triggerRef]);
 return <>{mobile&&<button className="sidebar-backdrop" tabIndex={-1} aria-label="Dismiss sidebar" onClick={onClose}/>}<aside id="workspace-sidebar" className="sidebar" ref={asideRef} aria-label="Workspace navigation" role={mobile?'dialog':undefined} aria-modal={mobile?true:undefined} onKeyDown={event=>{
  if(event.key==='Escape'){event.preventDefault();onClose();triggerRef.current?.focus()}
  if(mobile&&event.key==='Tab'){const controls=asideRef.current?.querySelectorAll<HTMLButtonElement>('button:not(:disabled),a[href]');if(!controls?.length)return;const first=controls[0],last=controls[controls.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus()}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus()}}
 }}><div className="sidebar-top"><button className="brand brand-home" onClick={onHome} aria-label="Back to PaisaPilot home"><PilotMark/><span>PaisaPilot<small>YOUR MONEY NAVIGATOR</small></span></button><button ref={closeRef} className="sidebar-close" aria-label="Close sidebar" onClick={()=>{onClose();triggerRef.current?.focus()}}><PanelLeftClose size={18}/></button></div><div className="workspace">WORKSPACE</div><nav aria-label="Finance tools">{items.map(([name,Icon])=><button key={name} className={`nav-item ${(page===name||(name==='Explore'&&['Market Lab','Business Desk','Currency','Credit Coach','Learn'].includes(page)))?'active':''}`} aria-current={page===name?'page':undefined} onClick={()=>{onChoose(name);if(mobile)onClose()}}><Icon size={18}/>{name}</button>)}</nav><button className="back-home" onClick={onHome}>← Back to home</button><div className="side-note"><i/>{privateMode?'Private workspace':'Demo / sign-in pending'}<small>{privateMode?'Your saved records':'Use sample data only'}</small></div></aside></>
}
