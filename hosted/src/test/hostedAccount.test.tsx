import {beforeEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import Panel from '../HostedAccountPanel';
import {api} from '../api';
vi.mock('../api',()=>({api:vi.fn()}));
const mock=vi.mocked(api);
beforeEach(()=>{mock.mockReset()});
it('uses top-level managed sign-in and never asks for a password',async()=>{mock.mockResolvedValue({workspace_mode:'demo',signed_in:false,assistant:{configured:true}} as never);render(<Panel onChange={vi.fn()}/>);const link=await screen.findByRole('link',{name:'Sign in with ChatGPT'});expect(link).toHaveAttribute('href','/signin-with-chatgpt?return_to=%2F%3Fworkspace%3Dprivate');expect(link).toHaveAttribute('target','_top');expect(screen.queryByLabelText('Password')).not.toBeInTheDocument()});
it('lets a signed-in user switch between sample and private workspaces',async()=>{mock.mockResolvedValue({workspace_mode:'demo',signed_in:true,assistant:{configured:true}} as never);const changed=vi.fn();render(<Panel onChange={changed}/>);fireEvent.click(await screen.findByRole('button',{name:'Use my private workspace'}));expect(localStorage.getItem('paisapilot-mode')).toBe('private');fireEvent.click(screen.getByRole('button',{name:'Try sample workspace'}));expect(localStorage.getItem('paisapilot-mode')).toBe('demo');expect(changed).toHaveBeenCalledTimes(2)});
