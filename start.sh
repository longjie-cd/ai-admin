#!/bin/bash

BACKEND_PORT=8000
FRONTEND_PORT=5173

kill_port() {
  local port=$1
  local pid
  pid=$(lsof -ti tcp:"$port")
  if [ -n "$pid" ]; then
    echo "Killing process on port $port (PID $pid)"
    kill -9 "$pid"
  fi
}

kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT

source venv/bin/activate

echo "Starting backend on port $BACKEND_PORT..."
uvicorn api.main:app --reload --port $BACKEND_PORT &
BACKEND_PID=$!

echo "Starting frontend on port $FRONTEND_PORT..."
cd vue && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:$BACKEND_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo ""
echo "Press Ctrl+C to stop both services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
