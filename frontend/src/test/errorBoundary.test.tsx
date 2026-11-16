import {it,expect,vi} from 'vitest';
import {render,screen} from '@testing-library/react';
import {ErrorBoundary} from '../ErrorBoundary';
it('shows a recoverable fallback rather than a blank application',()=>{
 const errors=vi.spyOn(console,'error').mockImplementation(()=>{});
 const expected=(event:ErrorEvent)=>{if(event.error?.message==='Unexpected render failure')event.preventDefault()};
 window.addEventListener('error',expected);
 function Broken(){throw new Error('Unexpected render failure');return null}
 try{render(<ErrorBoundary><Broken/></ErrorBoundary>);expect(screen.getByRole('alert')).toHaveTextContent('This view couldn’t load.');expect(screen.getByRole('button',{name:'Refresh PaisaPilot'})).toBeInTheDocument()}
 finally{window.removeEventListener('error',expected);errors.mockRestore()}
});
