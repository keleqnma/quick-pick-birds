@echo off
chcp 65001 >nul
title Quick Pick Birds - 观鸟照片识别应用

echo ========================================
echo   Quick Pick Birds - 观鸟照片识别
echo ========================================
echo.

:: 检查后端是否已在运行
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] 后端服务已在运行
) else (
    echo [→] 正在启动后端服务...
    cd /d "%~dp0backend"
    start "Quick Pick Birds - 后端服务" cmd /k "title 后端服务 && echo 后端服务启动中... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    timeout /t 3 /nobreak >nul
)

:: 启动 Electron 桌面应用
echo [→] 正在启动桌面应用...
cd /d "%~dp0frontend"
start "Quick Pick Birds - 桌面应用" npm run dev:electron

echo.
echo ========================================
echo   应用启动完成!
echo ========================================
echo.
echo   后端服务：http://localhost:8000
echo   API 文档：http://localhost:8000/docs
echo.
echo   提示：
echo   - 按 Ctrl+O 打开文件夹扫描
echo   - 按 F12 打开开发者工具
echo   - 按 Ctrl+Q 退出应用
echo.
echo   按任意键打开浏览器查看 API 文档...
pause >nul
start http://localhost:8000/docs
