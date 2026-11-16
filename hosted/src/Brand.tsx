export function PilotMark({className=""}:{className?:string}) {
 return <svg className={className} viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M6 30V10a4 4 0 0 1 4-4h13c8 0 13 4 13 11s-5 11-13 11H17v6H6Z" fill="currentColor"/><path d="m15 14 13 3-13 5 3-5-3-3Z" fill="var(--mark-cutout, #f5f6fa)"/></svg>
}

export function Pip({compact=false}:{compact?:boolean}) {
 return <svg className={compact?"pip-art compact":"pip-art"} viewBox="0 0 640 680" role="img" aria-label="Pip, PaisaPilot’s silver robot navigator with a violet visor and rupee badge">
 <defs>
 <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#fff"/><stop offset=".34" stopColor="#eff0fa"/><stop offset=".64" stopColor="#a4a8c1"/><stop offset=".83" stopColor="#f8f7ff"/><stop offset="1" stopColor="#7f849e"/></linearGradient>
 <linearGradient id="visor" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#9e8bff"/><stop offset=".45" stopColor="#483392"/><stop offset="1" stopColor="#151d36"/></linearGradient>
 <linearGradient id="purple" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#b9a5ff"/><stop offset=".5" stopColor="#7657f6"/><stop offset="1" stopColor="#4327a9"/></linearGradient>
 <radialGradient id="shine"><stop stopColor="white" stopOpacity=".6"/><stop offset="1" stopColor="white" stopOpacity="0"/></radialGradient>
 <filter id="shadow"><feGaussianBlur stdDeviation="14"/></filter>
 </defs>
 <ellipse cx="332" cy="610" rx="143" ry="20" fill="#080d1d" opacity=".28" filter="url(#shadow)"/>
 <g className="pip-body">
 <path d="M230 416c-37 9-67 51-51 76 12 20 41 9 61-13l32-41" fill="url(#metal)" stroke="#cbd0e5" strokeWidth="2"/>
 <path d="m407 410 42-45c16-17 40-13 45 5 7 24-20 66-53 80" fill="url(#metal)"/>
 <g transform="rotate(16 482 338)"><rect x="460" y="298" width="47" height="77" rx="23" fill="url(#metal)"/><path d="M474 312v21m13-25v22m12-16v22" stroke="#a1a5c1" strokeWidth="3" strokeLinecap="round"/></g>
 <path d="m270 495-15 51c-4 18 1 31 24 34l31-1 10-75m48-4 7 51c1 19 15 26 34 19l22-11-27-73" fill="url(#metal)" stroke="#c5c8db" strokeWidth="2"/>
 <path d="M246 437c0-47 33-69 80-69 59 0 102 36 102 80 0 63-32 83-91 83-57 0-91-28-91-94Z" fill="url(#metal)"/>
 <path d="M274 431c0-27 25-41 57-41 36 0 69 22 69 53 0 41-21 60-64 60-40 0-62-23-62-72Z" fill="#171f39"/>
 <circle cx="336" cy="448" r="34" fill="url(#purple)"/><text x="336" y="463" textAnchor="middle" fill="white" fontFamily="Arial,sans-serif" fontSize="44">₹</text>
 <rect x="286" y="364" width="87" height="29" rx="14" fill="#959ab5"/>
 <rect x="184" y="224" width="37" height="80" rx="18" fill="url(#purple)"/><rect x="436" y="222" width="34" height="78" rx="17" fill="url(#purple)"/>
 <path d="M206 255c0-84 47-131 121-131 88 0 130 51 130 135v27c0 68-52 101-126 101-79 0-125-38-125-108Z" fill="url(#metal)" stroke="#e9eafa" strokeWidth="2"/>
 <path d="M229 255c0-47 34-76 98-76 65 0 106 25 106 75v28c0 42-36 65-101 65-65 0-103-25-103-67Z" fill="#192038"/>
 <path d="M236 253c0-40 31-66 90-66 60 0 99 23 99 65v27c0 36-32 59-94 59s-95-22-95-59Z" fill="url(#visor)"/>
 <path d="M257 235c28-36 88-39 128-17" stroke="white" strokeWidth="7" opacity=".2" strokeLinecap="round"/>
 <path d="M274 273q10-19 21 0m67 0q10-19 21 0" stroke="#e1dbff" strokeWidth="7" strokeLinecap="round" fill="none"/>
 <path d="M316 295q13 12 27 0" stroke="#d5caff" strokeWidth="5" strokeLinecap="round" fill="none"/>
 <ellipse cx="259" cy="174" rx="55" ry="37" fill="url(#shine)"/>
 <path d="M329 126v-32" stroke="#cfd2e6" strokeWidth="9" strokeLinecap="round"/><circle cx="329" cy="86" r="13" fill="url(#purple)"/><circle cx="325" cy="82" r="4" fill="#e6deff"/>
 </g>
 <g className="coin coin-one"><ellipse cx="133" cy="355" rx="31" ry="36" fill="#42357c" transform="rotate(-20 133 355)"/><ellipse cx="128" cy="351" rx="29" ry="35" fill="url(#purple)" transform="rotate(-20 128 351)"/><text x="127" y="363" fill="#e4dbff" textAnchor="middle" fontSize="34" fontFamily="Arial">₹</text></g>
 <g className="coin coin-two"><circle cx="495" cy="196" r="27" fill="url(#metal)"/><path d="m483 196 9 9 16-18" fill="none" stroke="#7657f6" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round"/></g>
 </svg>
}
