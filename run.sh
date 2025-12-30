# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Set PYTHONPATH to the current directory so 'app' can be found
export PYTHONPATH=$PYTHONPATH:.

# Define the port
PORT=${PORT:-8080}

echo "Starting PowerCV Server on port $PORT..."

# Run uvicorn with settings that avoid PermissionErrors and ModuleNotFoundErrors
# --reload-dir app: only watch the app directory to avoid permission issues in .config or other home dirs
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload --reload-dir app
