import {Component,type ReactNode} from 'react';
export class ErrorBoundary extends Component<{children:ReactNode},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true}}
 render(){return this.state.failed?<main className="panel" style={{maxWidth:620,margin:'80px auto',padding:35}} role="alert"><h1>This view couldn’t load.</h1><p>Your saved records stay on the server. Refresh to try again; unsaved edits may be lost.</p><button className="primary-btn" onClick={()=>window.location.reload()}>Refresh PaisaPilot</button></main>:this.props.children}
}
