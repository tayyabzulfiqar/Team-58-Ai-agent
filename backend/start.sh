#!/bin/bash

pip install -r requirements.txt
uvicorn scripts.api.server:app --host 0.0.0.0 --port $PORT
