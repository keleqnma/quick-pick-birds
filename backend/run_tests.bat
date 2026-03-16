@echo off
REM 后端单元测试运行脚本
REM 用法：run_tests.bat

echo ========================================
echo  Quick Pick Birds - 后端单元测试
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 pytest 是否安装
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo [错误] pytest 未安装，正在安装...
    python -m pip install pytest pytest-asyncio httpx
)

REM 运行测试
echo [信息] 开始运行测试...
python -m pytest tests/ -v --tb=short %*

if errorlevel 1 (
    echo.
    echo ========================================
    echo  测试失败！
    echo ========================================
    exit /b 1
) else (
    echo.
    echo ========================================
    echo  所有测试通过！
    echo ========================================
    exit /b 0
)
