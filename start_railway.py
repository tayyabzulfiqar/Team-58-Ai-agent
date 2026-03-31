#!/usr/bin/env python3
"""Startup script with env vars baked in"""
import os
import sys

# Force set env vars (Railway isn't passing them correctly)
os.environ['BASE_URL'] = 'https://api.groq.com/openai/v1'
os.environ['MODEL'] = 'llama-3.3-70b-versatile'
# API_KEY must come from Railway dashboard

# Import and run server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.api.server import app
import uvicorn

port = int(os.environ.get("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
