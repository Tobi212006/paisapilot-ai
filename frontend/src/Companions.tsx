import {useEffect,useState} from "react";
import {ArrowUpRight,ChevronLeft,ChevronRight} from "lucide-react";
import {Pip} from "./Brand";

export type Friend="pip"|"card"|"mint"|"shield";
const crew:{id:Friend;name:string;role:string;page:string;copy:string}[]=[
 {id:"pip",name:"Pip",role:"Your money navigator",page:"Overview",copy:"A fresh day, a clear plan. Let’s find your next small money move."},
 {id:"mint",name:"Mint",role:"Your savings sidekick",page:"Goals",copy:"A little set aside today can make room for tomorrow’s plans."},
 {id:"card",name:"Chip",role:"Your credit card coach",page:"Credit Coach",copy:"Know your statement. Understand your balance. Keep credit in perspective."},
 {id:"shield",name:"Sentinel",role:"Your payment safety guide",page:"UPI Safety",copy:"Pause before you pay. Let’s take a second look at suspicious wording."}
];
export function timeFriend(hour:number):Friend{return hour>=5&&hour<12?"pip":hour>=12&&hour<17?"mint":hour>=17&&hour<22?"card":"shield"}
export function FriendArt({friend}:{friend:Friend}){
 if(friend==="pip")return <Pip compact/>;
 return <svg className={`friend-art friend-${friend}`} viewBox="0 0 280 240" role="img" aria-label={friend==="card"?"Chip, a friendly violet credit card character":friend==="mint"?"Mint, a smiling silver savings jar character":"Sentinel, a friendly payment shield character"}>
 <ellipse cx="140" cy="215" rx="71" ry="8" fill="#10182b" opacity=".1"/>
 <g className="friend-float"><path d="M86 160 68 182m126-25 20 18" stroke="#9e8bcf" strokeWidth="13" strokeLinecap="round"/><path d="m117 188-8 17m54-17 9 17" stroke="#a9a3c5" strokeWidth="13" strokeLinecap="round"/>
 {friend==="card"?<><rect x="53" y="61" width="177" height="125" rx="23" fill="#483183" transform="rotate(-8 140 120)"/><rect x="48" y="53" width="177" height="125" rx="23" fill="#8b6bf8" transform="rotate(-8 140 120)"/><path d="m66 73 91-12" stroke="#d8ccff" strokeWidth="3" opacity=".55"/><rect x="71" y="83" width="32" height="24" rx="5" fill="#ead8ac" transform="rotate(-8 87 95)"/><path d="m77 94 20-3m-12-6 3 20" stroke="#b59c66"/><text x="182" y="89" fill="#eee8ff" fontSize="23" fontFamily="Arial">₹</text><path d="m77 155 35-5m7-1 16-2" stroke="#c7b3ff" strokeWidth="4" strokeLinecap="round"/></>:friend==="mint"?<><rect x="85" y="68" width="116" height="129" rx="34" fill="#c6cbdc"/><rect x="78" y="62" width="116" height="129" rx="34" fill="#e2e5ee"/><rect x="85" y="54" width="102" height="22" rx="9" fill="#a99be0"/><path d="M115 65h44" stroke="#71628e" strokeWidth="5" strokeLinecap="round"/><circle cx="139" cy="30" r="20" fill="#bca6ff"/><text x="139" y="39" textAnchor="middle" fill="#5b3dad" fontSize="26" fontFamily="Arial">₹</text><path d="M93 89v53" stroke="white" strokeWidth="6" opacity=".7" strokeLinecap="round"/><path d="M103 173h68" stroke="#a99be0" strokeWidth="4" opacity=".6"/></>:<><path d="m140 42 76 27v64c0 36-38 62-76 77-38-15-76-41-76-77V69Z" fill="#535c80"/><path d="m135 35 76 27v64c0 36-38 62-76 77-38-15-76-41-76-77V62Z" fill="#b8acd9"/><path d="m135 51 60 21v53c0 25-29 49-60 63-31-14-60-38-60-63V72Z" fill="#202b48"/><path d="m118 158 13 11 24-27" stroke="#bda8ff" strokeWidth="6" strokeLinecap="round" fill="none"/></>}
 <path d="M111 122q6-12 13 0m28 0q6-12 13 0" stroke={friend==="mint"?"#53516e":"#f5efff"} strokeWidth="4" strokeLinecap="round" fill="none"/><path d="M132 137q7 7 14 0" stroke={friend==="mint"?"#53516e":"#f5efff"} strokeWidth="3" strokeLinecap="round" fill="none"/>
 </g><path d="m38 44 3 9 9 3-9 3-3 9-3-9-9-3 9-3Zm192 134 2 6 6 2-6 2-2 6-2-6-6-2 6-2Z" fill="#b49afc"/>
 </svg>
}
export function Companion({page="",onOpen}:{page?:string;onOpen?:(page:string)=>void}){
 const[clock,setClock]=useState(()=>new Date()),[manual,setManual]=useState<Friend|null>(null);
 useEffect(()=>{const id=window.setInterval(()=>setClock(new Date()),60000);return()=>window.clearInterval(id)},[]);
 const hour=Number(new Intl.DateTimeFormat("en-GB",{timeZone:"Asia/Kolkata",hour:"2-digit",hourCycle:"h23"}).format(clock));
 const context:Friend|null=page==="Credit Coach"?"card":page==="Goals"||page==="Budget"?"mint":page==="UPI Safety"?"shield":null;
 const selected=manual||context||timeFriend(hour),index=crew.findIndex(f=>f.id===selected),friend=crew[index];
 return <section className="companion-banner" aria-label="Money companion"><div className="companion-portrait"><FriendArt friend={selected}/></div><div className="companion-message"><span className="section-kicker">{context?"HERE FOR THIS STEP":`${hour<5?"TAKE IT EASY TONIGHT":hour<12?"GOOD MORNING":hour<17?"GOOD AFTERNOON":hour<22?"GOOD EVENING":"TAKE IT EASY TONIGHT"} · INDIA TIME`}</span><h3>Meet {friend.name}. <span>{friend.role}.</span></h3><p>{friend.copy}</p>{onOpen&&<button className="text-link" onClick={()=>onOpen(friend.page)}>Explore with {friend.name} <ArrowUpRight size={16}/></button>}</div><div className="companion-controls"><button aria-label="Previous companion" onClick={()=>setManual(crew[(index+3)%4].id)}><ChevronLeft size={17}/></button><button aria-label="Next companion" onClick={()=>setManual(crew[(index+1)%4].id)}><ChevronRight size={17}/></button><button className={manual?"":"auto-active"} onClick={()=>setManual(null)}>Auto</button></div></section>
}
export function CrewSection({onOpen}:{onOpen:(page:string)=>void}){return <section className="crew-section section-wrap"><div className="section-heading"><div><span className="section-kicker">A LITTLE COMPANY FOR EVERY MONEY MOMENT</span><h2>Meet your money crew.</h2></div><p>Pip stays at the heart of it. A few friends bring a fresh perspective to savings, credit, and payment safety.</p></div><div className="crew-grid">{crew.map(f=><button key={f.id} className="crew-card" onClick={()=>onOpen(f.page)}><FriendArt friend={f.id}/><h3>{f.name} <ArrowUpRight size={18}/></h3><p>{f.role}</p></button>)}</div><Companion onOpen={onOpen}/><p className="crew-footnote">Companions change with India time and the screen you’re using. You can choose another anytime. Characters offer education, not account monitoring.</p></section>}
