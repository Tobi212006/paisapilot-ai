import {useState} from "react";
import App from "./App";
import Landing from "./Landing";
import "./experience.css";
import "./connections.css";
import "./midnight.css";
import {MotionSettings} from "./MotionSettings";
export default function Experience(){
 const[workspace,setWorkspace]=useState<string|null>(()=>new URLSearchParams(location.search).get("workspace")==="private"?"Overview":null);
 return <MotionSettings>{workspace?<App initialPage={workspace} onHome={()=>{setWorkspace(null);window.scrollTo(0,0)}}/>:<Landing onOpen={(page="Overview")=>setWorkspace(page)}/>}</MotionSettings>;
}
