@echo off
echo ========================================
echo Quick Pick Birds - 启动脚本
echo ========================================

echo.
echo [1/3] 启动后端服务...
cd /d "%~dp0backend"
call venv\Scripts\activate
start "Quick Pick Birds - Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [2/3] 启动 Electron 桌面应用...
cd /d "%~dp0frontend"
start "Quick Pick Birds - Electron" cmd /k "npm run dev:electron"

echo [3/3] 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 服务启动完成!
echo ========================================
echo 后端：http://localhost:8000
echo API 文档：http://localhost:8000/docs
echo.
echo Electron 桌面应用即将启动，请稍候...
