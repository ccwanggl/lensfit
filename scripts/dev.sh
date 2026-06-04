#!/bin/bash
# Start LensFit in development mode: backend + frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting LensFit development servers...${NC}"

# Check Python venv
if [ ! -d "engine/.venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd engine && python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
    cd ..
fi

# Check node_modules
if [ ! -d "apps/desktop/node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    cd apps/desktop && npm install
    cd ../..
fi

# Check database
if [ ! -f "lensfit.db" ]; then
    echo -e "${YELLOW}Initializing database...${NC}"
    source engine/.venv/bin/activate
    python database/import_scripts/import_seed.py
fi

# Start backend
echo -e "${GREEN}Starting backend on port 8765...${NC}"
source engine/.venv/bin/activate
python -m engine.lensfit.api.server --port 8765 --db sqlite:///lensfit.db &
BACKEND_PID=$!

# Wait for backend
for i in {1..30}; do
    if curl -s http://127.0.0.1:8765/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend ready!${NC}"
        break
    fi
    sleep 0.5
done

# Start frontend
echo -e "${GREEN}Starting frontend dev server...${NC}"
cd apps/desktop
npm run dev &
FRONTEND_PID=$!

cd ../..

echo ""
echo -e "${GREEN}LensFit is running!${NC}"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://127.0.0.1:8765"
echo ""
echo "Press Ctrl+C to stop both servers"

# Trap Ctrl+C
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    wait 2>/dev/null || true
    echo -e "${GREEN}Done.${NC}"
    exit 0
}
trap cleanup INT TERM

wait
