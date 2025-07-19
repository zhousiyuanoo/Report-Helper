@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo 🐂 牛马日报助手 - 启动脚本
echo ================================================
echo.

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo 📁 当前目录: %CD%
echo.

REM 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.6或更高版本
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%
echo.

REM 检查虚拟环境
echo 🔍 检查虚拟环境...
if exist "venv\Scripts\activate.bat" (
    echo ✅ 找到虚拟环境
    echo 🚀 激活虚拟环境...
    call "venv\Scripts\activate.bat"
    if errorlevel 1 (
        echo ❌ 虚拟环境激活失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未找到虚拟环境，使用系统Python环境
    echo 💡 建议运行 setup.bat 创建虚拟环境
)
echo.

REM 检查依赖包
echo 🔍 检查依赖包...
python -c "import PyQt5, requests, openai, dotenv, psutil" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少必要的依赖包
    echo 🔧 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        echo 💡 请检查网络连接或手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 依赖包检查通过
)
echo.

REM 检查配置文件
echo 🔍 检查配置文件...
if not exist "config.json" (
    echo ⚠️  配置文件不存在，将使用默认配置
)

if not exist ".env" (
    echo ⚠️  环境变量文件(.env)不存在
    if exist ".env.example" (
        echo 💡 发现模板文件，正在复制...
        copy ".env.example" ".env" >nul
        echo ✅ 已创建.env文件，请编辑配置API密钥等信息
        echo 📝 配置文件位置: %CD%\.env
    ) else (
        echo ❌ 未找到.env.example模板文件
    )
    echo.
    echo 🔧 请配置以下信息后重新启动:
    echo    - OpenAI API密钥 (OPENAI_API_KEY)
    echo    - 飞书应用配置 (FEISHU_APP_ID, FEISHU_APP_SECRET)
    echo.
    set /p "continue=是否继续启动应用? (y/N): "
    if /i not "!continue!"=="y" (
        echo 👋 启动已取消
        pause
        exit /b 0
    )
) else (
    echo ✅ 环境变量文件存在
)
echo.

REM 创建必要的目录
echo 🔍 检查目录结构...
if not exist "data" mkdir "data"
if not exist "logs" mkdir "logs"
if not exist "backup" mkdir "backup"
echo ✅ 目录结构检查完成
echo.

REM 启动应用程序
echo 🚀 启动牛马日报助手...
echo ================================================
echo.

REM 设置环境变量
set PYTHONPATH=%CD%
set PYTHONIOENCODING=utf-8

REM 启动主程序
python main.py

REM 检查退出代码
set EXIT_CODE=%ERRORLEVEL%
echo.
echo ================================================
if %EXIT_CODE% equ 0 (
    echo ✅ 应用程序正常退出
) else (
    echo ❌ 应用程序异常退出 (退出代码: %EXIT_CODE%)
    echo 💡 请检查logs目录下的日志文件获取详细错误信息
    echo 📁 日志目录: %CD%\logs
)
echo ================================================

REM 如果是双击运行，暂停以查看输出
echo %CMDCMDLINE% | find /i "%~0" >nul
if not errorlevel 1 (
    echo.
    echo 按任意键退出...
    pause >nul
)

exit /b %EXIT_CODE%