import {beforeEach,describe,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import App from '../App';
import {MotionSettings} from '../MotionSettings';
import {api} from '../api';
vi.mock('../api',()=>({api:vi.fn(),isSignedIn:()=>false,setAccessToken:vi.fn()}));
vi.mock('../authClient',()=>({supabase:null,authConfigurationError:''}));
const mockApi=vi.mocked(api);
beforeEach(()=>{mockApi.mockReset();mockApi.mockImplementation(async path=>{
 if(path.startsWith('/api/planning/month'))return {month:'2026-11',income:300,gross_expenses:100,refunds:0,net_spending:100,recorded_cash_flow:200,transaction_count:1,transfers_excluded:0,mode:'sample',partial_month:true,coverage:{first:'2026-11-01',last:'2026-11-01',note:'Recorded entries only'},comparison:null,budgets:[],facts:[],transactions:[]} as never;
 if(path==='/api/review/batches')return [] as never;
 if(path==='/api/dashboard')return {total_spent:100,total_income:300,net:200,transaction_count:1,by_category:[{category:'Food',total:100}],currency:'INR',data_label:'shared local demo records'} as never;
 if(path==='/api/goals')return [{id:1,title:'Buffer',target_amount:500,saved_amount:100}] as never;
 if(path==='/api/transactions')return [] as never;
 if(path==='/api/connections')return {workspace_mode:'demo',supabase:{configured:false},upstox:{configured:false},assistant:{configured:false}} as never;
 if(path==='/api/safety/check')return {risk_band:'review',risk_score:35,rules_triggered:['Sensitive credential requested'],disclaimer:'Educational screening'} as never;
 if(path==='/api/market/indicators')return {sma:111,rsi_14_approx:88.24,data_mode:'Historical prices'} as never;
 if(path==='/api/business/gst-estimate')return {total:11800,cgst:900,sgst:900,igst:0,disclaimer:'Illustrative estimate'} as never;
 return {} as never;
})});
function mount(){return render(<MotionSettings><App onHome={vi.fn()}/></MotionSettings>)}
describe('workspace system flow',()=>{
 it('loads real API totals, visits every screen, and toggles sidebar',async()=>{mount();await screen.findByText('API connected');expect(screen.getAllByText('₹100.00').length).toBeGreaterThan(0);for(const name of ['Transactions','Budget','UPI Safety','Market Lab','Business Desk','Goals','Learn','Currency','Credit Coach','Connections','Overview']){if(['Market Lab','Business Desk','Learn','Currency','Credit Coach'].includes(name))fireEvent.click(screen.getByRole('button',{name:'Explore'}));fireEvent.click(screen.getByRole('button',{name}));expect(screen.getByRole('heading',{name,level:1})).toBeInTheDocument()}fireEvent.click(screen.getByRole('button',{name:'Close sidebar'}));expect(screen.queryByRole('navigation',{name:'Finance tools'})).not.toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'Open sidebar'}));expect(screen.getByRole('navigation',{name:'Finance tools'})).toBeInTheDocument()});
 it('runs safety, market and GST and saves a goal',async()=>{mount();await screen.findByText('API connected');fireEvent.click(screen.getByRole('button',{name:'UPI Safety'}));fireEvent.click(screen.getByRole('button',{name:'Analyse message'}));expect(await screen.findByText('Warning level: review')).toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'Explore'}));fireEvent.click(screen.getByRole('button',{name:'Market Lab'}));fireEvent.click(screen.getByRole('button',{name:'Calculate indicators'}));expect(await screen.findByText('SMA: 111')).toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'Explore'}));fireEvent.click(screen.getByRole('button',{name:'Business Desk'}));fireEvent.click(screen.getByRole('button',{name:'Calculate estimate'}));expect(await screen.findByText('Total: ₹11,800.00')).toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'Goals'}));fireEvent.click(screen.getByRole('button',{name:'Save goal'}));await screen.findByText('Goal saved.');expect(mockApi.mock.calls.some(([path,options])=>path==='/api/goals'&&options?.method==='POST')).toBe(true)});
 it('asks for sign-in without reporting an outage',async()=>{mockApi.mockRejectedValue(new Error('Sign in to access your private workspace.'));mount();expect(await screen.findByText('Sign-in required')).toBeInTheDocument();expect(screen.queryByText(/Backend unavailable/)).not.toBeInTheDocument()});
 it('reports backend outage visibly',async()=>{mockApi.mockRejectedValue(new Error('Backend unreachable'));mount();expect(await screen.findByText('API offline')).toBeInTheDocument();expect(screen.getByText(/Backend unavailable/)).toBeInTheDocument()});
 it('shows action failures and rejects invalid manual prices',async()=>{mount();await screen.findByText('API connected');fireEvent.click(screen.getByRole('button',{name:'Explore'}));fireEvent.click(screen.getByRole('button',{name:'Market Lab'}));fireEvent.change(screen.getByRole('textbox',{name:''}),{target:{value:'abc,0'}});fireEvent.click(screen.getByRole('button',{name:'Calculate indicators'}));await screen.findByText('Enter positive comma-separated prices.');fireEvent.click(screen.getByRole('button',{name:'Goals'}));mockApi.mockRejectedValueOnce(new Error('Goal rejected'));fireEvent.click(screen.getByRole('button',{name:'Save goal'}));await screen.findByText('Goal rejected')});
 it('refreshes workspace totals on a session change',async()=>{mount();await screen.findByText('API connected');const before=mockApi.mock.calls.length;window.dispatchEvent(new Event('paisapilot-session'));await waitFor(()=>expect(mockApi.mock.calls.length).toBeGreaterThan(before))});
 it('clears a safety conclusion when its input changes',async()=>{mount();await screen.findByText('API connected');fireEvent.click(screen.getByRole('button',{name:'UPI Safety'}));fireEvent.click(screen.getByRole('button',{name:'Analyse message'}));await screen.findByText('Warning level: review');fireEvent.change(screen.getByRole('textbox',{name:''}),{target:{value:'Never share your OTP.'}});expect(screen.queryByText('Warning level: review')).not.toBeInTheDocument()});

});
