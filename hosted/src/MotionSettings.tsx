import {createContext,useContext,useState,type ReactNode} from "react";
import {MotionConfig,useReducedMotion} from "framer-motion";
import {Pause,Play} from "lucide-react";

const Settings=createContext({paused:false,systemReduced:false,toggle:()=>{}});
export function useMotionSettings(){return useContext(Settings)}
export function MotionSettings({children}:{children:ReactNode}){
 const systemReduced=Boolean(useReducedMotion());
 const[manualPause,setManualPause]=useState(()=>{try{return localStorage.getItem('paisapilot-motion')==='paused'}catch{return false}});
 const paused=manualPause||systemReduced;
 function toggle(){setManualPause(value=>{const next=!value;try{localStorage.setItem('paisapilot-motion',next?'paused':'playing')}catch{}return next})}
 return <Settings.Provider value={{paused,systemReduced,toggle}}><MotionConfig reducedMotion={paused?'always':'user'}><div className="night-experience" data-motion={paused?'paused':'playing'}>{children}</div></MotionConfig></Settings.Provider>
}
export function MotionToggle(){const{paused,systemReduced,toggle}=useMotionSettings();return <button className="motion-toggle" onClick={toggle} disabled={systemReduced} aria-label={systemReduced?'Reduced motion enabled by your device':paused?'Resume animations':'Pause animations'} aria-pressed={paused} title={systemReduced?'Your device requests reduced motion':paused?'Resume animations':'Pause animations'}>{paused?<Play size={14}/>:<Pause size={14}/>}<span>{systemReduced?'Reduced motion':paused?'Motion paused':'Pause motion'}</span></button>}
