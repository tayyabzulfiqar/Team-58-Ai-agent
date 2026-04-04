pip install -r requirements.txt
#!/bin/bash
exec uvicorn scripts.api.server:app --host 0.0.0.0 --port $PORT --workers 2
