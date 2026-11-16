import {beforeEach,describe,it,expect,vi} from 'vitest';
import {api,setAccessToken,isSignedIn} from '../api';
beforeEach(()=>setAccessToken(''));
describe('API transport',()=>{
 it('attaches a bearer token and parses JSON',async()=>{setAccessToken('session');const fetch=vi.fn().mockResolvedValue(new Response('{"ok":true}'));vi.stubGlobal('fetch',fetch);expect(await api('/api/dashboard')).toEqual({ok:true});expect(fetch.mock.calls[0][1].headers.Authorization).toBe('Bearer session');expect(isSignedIn()).toBe(true)});
 it('does not attach auth when signed out',async()=>{const fetch=vi.fn().mockResolvedValue(new Response('[]'));vi.stubGlobal('fetch',fetch);await api('/api/goals');expect(fetch.mock.calls[0][1].headers.Authorization).toBeUndefined()});
 it.each([[401,'{"detail":"Sign in"}','Sign in'],[422,'{"detail":[]}', 'Check your inputs'],[500,'bad-json','Request failed (500)']])('handles HTTP %s',async(status,body,message)=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(body,{status})));await expect(api('/api/dashboard')).rejects.toThrow(message)});
 it('does not display data from the previous session',async()=>{let finish!:(r:Response)=>void;vi.stubGlobal('fetch',vi.fn().mockImplementation(()=>new Promise(r=>{finish=r})));const pending=api('/api/dashboard');setAccessToken('new-user');finish(new Response('{"private":"old"}'));await expect(pending).rejects.toThrow('Session changed')});
 it('does not emit redundant session events',()=>{const listener=vi.fn();window.addEventListener('paisapilot-session',listener);setAccessToken('same');setAccessToken('same');expect(listener).toHaveBeenCalledTimes(1);window.removeEventListener('paisapilot-session',listener)});
 it('normalizes network, timeout and malformed JSON failures',async()=>{vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('network')));await expect(api('/api/dashboard')).rejects.toThrow('Could not reach');vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new DOMException('timeout','TimeoutError')));await expect(api('/api/dashboard')).rejects.toThrow('timed out');vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response('invalid')));await expect(api('/api/dashboard')).rejects.toThrow('invalid response')});
 it('rejects non-API paths',async()=>{await expect(api('https://third-party.test')).rejects.toThrow('Invalid API path')});
});
