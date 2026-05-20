@echo off
REM 启动 The Station & Agent 应用

echo.
echo ====================================
echo   The Station & Agent
echo   应用启动脚本
echo ====================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

echo [✓] Python 已安装
echo.

REM 检查 MongoDB 服务
echo 检查 MongoDB 服务...
sc query MongoDB >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] MongoDB 服务已检测到
    net start MongoDB >nul 2>&1
    echo [✓] MongoDB 服务已启动
) else (
    echo [⚠] MongoDB 服务未检测到
    echo [提示] 请确保 mongod 正在运行，或从命令行启动：mongod
)

echo.
echo 正在启动 Flask 应用...
echo.

cd /d "%~dp0"
python app.py

pause

