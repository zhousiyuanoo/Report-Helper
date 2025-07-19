@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo 🐂 牛马日报助手 - 环境安装脚本
echo ================================================
echo.
echo 此脚本将自动安装运行环境和依赖包
echo 请确保您的计算机已连接到互联网
echo.
set /p "continue=是否继续安装? (Y/n): "
if /i "!continue!"=="n" (
    echo 👋 安装已取消
    pause
    exit /b 0
)

echo.
echo 🚀 开始安装...
echo ================================================
echo.

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo 📁 安装目录: %CD%
echo.

REM 检查Python是否安装
echo 🔍 步骤 1/8: 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.6或更高版本:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装最新版本的Python
    echo 3. 安装时请勾选 "Add Python to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%
echo.

REM 检查pip是否可用
echo 🔍 步骤 2/8: 检查pip包管理器...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: pip不可用
    echo 💡 尝试使用python -m pip...
    python -m pip --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ pip完全不可用，请重新安装Python
        pause
        exit /b 1
    ) else (
        echo ✅ 使用python -m pip
        set "PIP_CMD=python -m pip"
    )
) else (
    echo ✅ pip可用
    set "PIP_CMD=pip"
)
echo.

REM 创建虚拟环境
echo 🔍 步骤 3/8: 创建虚拟环境...
if exist "venv" (
    echo ⚠️  虚拟环境已存在
    set /p "recreate=是否重新创建虚拟环境? (y/N): "
    if /i "!recreate!"=="y" (
        echo 🗑️  删除现有虚拟环境...
        rmdir /s /q "venv"
        echo ✅ 现有虚拟环境已删除
    ) else (
        echo ➡️  跳过虚拟环境创建
        goto activate_venv
    )
)

echo 🔧 创建新的虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo ❌ 虚拟环境创建失败
    echo 💡 可能的解决方案:
    echo    1. 确保Python安装完整
    echo    2. 以管理员身份运行此脚本
    echo    3. 检查磁盘空间是否充足
    pause
    exit /b 1
)
echo ✅ 虚拟环境创建成功
echo.

:activate_venv
REM 激活虚拟环境
echo 🔍 步骤 4/8: 激活虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 虚拟环境激活脚本不存在
    pause
    exit /b 1
)

call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活
echo.

REM 升级pip
echo 🔍 步骤 5/8: 升级pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  pip升级失败，继续使用当前版本
) else (
    echo ✅ pip升级完成
)
echo.

REM 安装依赖包
echo 🔍 步骤 6/8: 安装依赖包...
if not exist "requirements.txt" (
    echo ❌ 错误: requirements.txt文件不存在
    echo 💡 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

echo 📦 正在安装依赖包，这可能需要几分钟...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败
    echo.
    echo 💡 可能的解决方案:
    echo    1. 检查网络连接
    echo    2. 尝试使用国内镜像源:
    echo       pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    echo    3. 手动安装各个包
    echo.
    set /p "retry=是否尝试使用清华镜像源重新安装? (Y/n): "
    if /i not "!retry!"=="n" (
        echo 🔄 使用清华镜像源重新安装...
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
        if errorlevel 1 (
            echo ❌ 镜像源安装也失败了
            pause
            exit /b 1
        )
    ) else (
        pause
        exit /b 1
    )
)
echo ✅ 依赖包安装完成
echo.

REM 创建必要的目录
echo 🔍 步骤 7/8: 创建项目目录...
set "DIRS=data logs backup"
for %%d in (%DIRS%) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo ✅ 创建目录: %%d
    ) else (
        echo ➡️  目录已存在: %%d
    )
)
echo.

REM 创建配置文件
echo 🔍 步骤 8/8: 创建配置文件...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ 已创建.env配置文件
    ) else (
        echo ⚠️  .env.example模板文件不存在
    )
) else (
    echo ➡️  .env文件已存在
)

if not exist "config.json" (
    echo ➡️  config.json将在首次运行时自动创建
) else (
    echo ➡️  config.json文件已存在
)
echo.

echo ================================================
echo 🎉 安装完成！
echo ================================================
echo.
echo ✅ 虚拟环境已创建并激活
echo ✅ 所有依赖包已安装
echo ✅ 项目目录结构已创建
echo ✅ 配置文件已准备
echo.
echo 📝 下一步操作:
echo.
echo 1. 编辑配置文件 .env，填入以下信息:
echo    📁 文件位置: %CD%\.env
echo    🔑 OpenAI API密钥 (OPENAI_API_KEY)
echo    🚀 飞书应用配置 (FEISHU_APP_ID, FEISHU_APP_SECRET)
echo.
echo 2. 启动应用程序:
echo    🖱️  双击运行: start.bat
echo    💻 命令行运行: python main.py
echo.
echo 📚 更多信息请查看 README.md 文件
echo.
echo 🔗 获取API密钥:
echo    OpenAI: https://platform.openai.com/api-keys
echo    飞书开放平台: https://open.feishu.cn/
echo.

set /p "open_config=是否现在打开配置文件进行编辑? (Y/n): "
if /i not "!open_config!"=="n" (
    echo 📝 正在打开配置文件...
    notepad ".env"
)

echo.
set /p "start_app=是否现在启动应用程序? (Y/n): "
if /i not "!start_app!"=="n" (
    echo 🚀 正在启动应用程序...
    call "start.bat"
) else (
    echo.
    echo 👋 安装完成，您可以稍后运行 start.bat 启动应用程序
    pause
)

exit /b 0