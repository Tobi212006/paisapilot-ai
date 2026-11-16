import '@testing-library/jest-dom/vitest';
import {afterEach,vi} from 'vitest';
import {cleanup} from '@testing-library/react';
afterEach(()=>{cleanup();localStorage.clear();vi.unstubAllGlobals();vi.unstubAllEnvs()});
Object.defineProperty(window,'matchMedia',{writable:true,value:vi.fn().mockImplementation(query=>({matches:false,media:query,onchange:null,addEventListener:vi.fn(),removeEventListener:vi.fn(),addListener:vi.fn(),removeListener:vi.fn(),dispatchEvent:vi.fn()}))});
window.scrollTo=vi.fn();
globalThis.IntersectionObserver=class{observe(){} unobserve(){} disconnect(){} takeRecords(){return []} root=null;rootMargin='0px';thresholds=[]} as unknown as typeof IntersectionObserver;
