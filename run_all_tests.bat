@echo off
REM 综合测试运行脚本 - 后端 + 前端
REM 用法：run_all_tests.bat

echo ========================================
echo  Quick Pick Birds - 完整测试套件
echo ========================================
echo.

cd /d "%~dp0"

set BACKEND_RESULT=0
set FRONTEND_RESULT=0

REM ================================
REM 后端测试
REM ================================
echo [1/2] 运行后端测试...
echo ----------------------------------------
cd backend
call run_tests.bat
set BACKEND_RESULT=%errorlevel%
cd ..

echo.

REM ================================
REM 前端测试
REM ================================
echo [2/2] 运行前端测试...
echo ----------------------------------------
cd frontend
call npm test
set FRONTEND_RESULT=%errorlevel%
cd ..

echo.
echo ========================================
echo  测试结果汇总
echo ========================================

if %BACKEND_RESULT% equ 0 (
    echo  后端测试：通过
) else (
    echo  后端测试：失败
)

if %FRONTEND_RESULT% equ 0 (
    echo  前端测试：通过
) else (
    echo  前端测试：失败
)

echo.

if %BACKEND_RESULT% equ 0 if %FRONTEND_RESULT% equ 0 (
    echo ========================================
    echo  所有测试通过！
    echo ========================================
    exit /b 0
) else (
    echo ========================================
    echo  部分测试失败！
    echo ========================================
    exit /b 1
)
