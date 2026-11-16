import {useEffect,useRef,useState} from "react";
import DarkVeil from "./vendor/react-bits/DarkVeil";
import {useMotionSettings} from "./MotionSettings";

export function Atmosphere(){
 const{paused}=useMotionSettings();
 const host=useRef<HTMLDivElement>(null);
 const[visible,setVisible]=useState(true),[pageVisible,setPageVisible]=useState(!document.hidden);
 useEffect(()=>{const observer=new IntersectionObserver(([entry])=>setVisible(entry.isIntersecting),{rootMargin:'100px'});if(host.current)observer.observe(host.current);const change=()=>setPageVisible(!document.hidden);document.addEventListener('visibilitychange',change);return()=>{observer.disconnect();document.removeEventListener('visibilitychange',change)}},[]);
 return <div className="midnight-atmosphere" ref={host} aria-hidden="true"><div className="aurora-fallback"/><DarkVeil color="#9270ff" speed={0.35} flow={0.8} warp={0.2} brightness={1.1} glow={0.8} grain={0.015} quality={0.55} dpr={1} intro={false} fade={0.12} mouseInteraction={!paused} mouseStrength={0.2} paused={paused||!visible||!pageVisible}/><div className="aurora-legibility"/></div>
}
