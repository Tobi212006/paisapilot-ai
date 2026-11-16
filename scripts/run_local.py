"""Run the private app or an isolated sample demo with one command."""
import argparse
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo',action='store_true',help='Build and serve isolated sample records; no private keys or account access.')
    parser.add_argument('--demo-ai',action='store_true',help='Enable only curated Pip learning topics in the demo; financial-summary sharing stays blocked.')
    parser.add_argument('--port',type=int,help='API/demo port; defaults to 8000 private or 8001 demo.')
    args=parser.parse_args()
    if args.demo_ai and not args.demo:
        parser.error('--demo-ai requires --demo.')
    root=Path(__file__).resolve().parents[1]
    backend=root/'backend'
    python=backend/('.venv/Scripts/python.exe' if os.name=='nt' else '.venv/bin/python')
    node=shutil.which('node')
    vite=root/'frontend/node_modules/vite/bin/vite.js'
    if not python.is_file() or not node or not vite.is_file():
        parser.error('Install backend and frontend dependencies first; see docs/RUNNING.md.')
    port=args.port or (8001 if args.demo else 8000)
    ports=[port] if args.demo else [port,5174]
    if len(set(ports))!=len(ports) or any(not 1024<=p<=65535 for p in ports):
        parser.error('Choose a distinct port between 1024 and 65535.')
    for candidate in ports:
        with socket.socket() as check:
            try:check.bind(('127.0.0.1',candidate))
            except OSError:parser.error(f'Port {candidate} is already in use. Stop the existing PaisaPilot server or choose --port for the demo.')
    env=os.environ.copy()
    if args.demo:
        env['DEMO_LEARNING_AI']='true' if args.demo_ai else 'false'
        env.update(VITE_API_BASE_URL='/',VITE_SUPABASE_URL='',VITE_SUPABASE_PUBLISHABLE_KEY='')
        for name in ('SUPABASE_URL','SUPABASE_PUBLISHABLE_KEY','GEMINI_API_KEY','GROQ_API_KEY','UPSTOX_ANALYTICS_TOKEN'):
            env.pop(name,None)
        print('Building the sample demo. Browser credentials and private records are excluded.',flush=True)
        result=subprocess.run([node,str(root/'frontend/node_modules/typescript/bin/tsc'),'--noEmit'],cwd=root/'frontend',env=env)
        if result.returncode:return result.returncode
        result=subprocess.run([node,str(vite),'build','--outDir','demo-dist'],cwd=root/'frontend',env=env)
        if result.returncode:return result.returncode
    else:
        env['VITE_API_BASE_URL']=f'http://127.0.0.1:{port}'
    children=[]
    try:
        target='app.demo:app' if args.demo else 'app.main:app'
        children.append(subprocess.Popen([str(python),'-m','uvicorn',target,'--host','127.0.0.1','--port',str(port)],cwd=backend,env=env))
        if not args.demo:
            children.append(subprocess.Popen([node,str(vite),'--host','127.0.0.1','--port','5174'],cwd=root/'frontend',env=env))
        print(f'PaisaPilot: http://127.0.0.1:{port if args.demo else 5174}/ — keep this terminal open; Ctrl+C stops the app.',flush=True)
        while all(child.poll() is None for child in children):time.sleep(.5)
        return next((child.returncode for child in children if child.returncode),0)
    except KeyboardInterrupt:
        return 0
    finally:
        for child in children:
            if child.poll() is None:child.terminate()
        for child in children:
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()


if __name__=='__main__':
    sys.exit(main())
