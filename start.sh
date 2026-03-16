#!/bin/bash

echo "========================================"
echo "Quick Pick Birds - 启动脚本"
echo "========================================"

echo ""
echo "[1/3] 启动后端服务..."
cd "$(dirname "$0")/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "[2/3] 启动前端服务..."
cd "$(dirname "$0")/frontend"
npm run dev &
FRONTEND_PID=$!

echo "[3/3] 等待服务启动..."
sleep 3

echo ""
echo "========================================"
echo "服务启动完成!"
echo "========================================"
echo "前端：http://localhost:5173"
echo "后端：http://localhost:8000"
echo "API 文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

wait $BACKEND_PID $FRONTEND_PID
