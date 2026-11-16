"""Isolated sample workspace; optional server-only AI for curated topics."""
import os
from pathlib import Path
from dotenv import dotenv_values

os.environ['LOAD_ENV_FILE']='false'
os.environ['APP_ENV']='development'
os.environ['DEMO_MODE']='true'
os.environ['PUBLIC_DEMO']='true'
for name in ('SUPABASE_URL','SUPABASE_PUBLISHABLE_KEY','GEMINI_API_KEY','GROQ_API_KEY','UPSTOX_ANALYTICS_TOKEN'):
    os.environ.pop(name,None)
if os.getenv('DEMO_LEARNING_AI','false').lower()=='true':
    settings=dotenv_values(Path(__file__).resolve().parents[1]/'.env')
    for name in ('GEMINI_API_KEY','GEMINI_MODEL'):
        if settings.get(name):os.environ[name]=settings[name]
os.environ['DATABASE_PATH']=os.getenv('DEMO_DATABASE_PATH',str(Path(__file__).resolve().parents[1]/'demo.db'))

from fastapi.staticfiles import StaticFiles
from .main import app

directory=Path(__file__).resolve().parents[2]/'frontend'/'demo-dist'
if not directory.is_dir():
    raise RuntimeError('Build the demo first: python scripts/run_local.py --demo')
app.mount('/',StaticFiles(directory=directory,html=True),name='sample-workspace')
