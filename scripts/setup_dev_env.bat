@echo off
REM 开发环境设置脚本 (Windows)

echo ==========================================
echo DSL Schema项目 - 开发环境设置
echo ==========================================

REM 检查Python版本
echo 检查Python版本...
python --version
if errorlevel 1 (
    echo 错误: Python未安装
    exit /b 1
)

REM 创建虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装Python依赖
echo 安装Python依赖...
python -m pip install --upgrade pip
pip install -r code\requirements.txt

REM 安装TypeScript依赖
if exist "code\package.json" (
    echo 安装TypeScript依赖...
    cd code
    call npm install
    cd ..
)

REM 检查PostgreSQL
echo 检查PostgreSQL...
where psql >nul 2>&1
if errorlevel 1 (
    echo 警告: PostgreSQL未安装，请手动安装
) else (
    echo PostgreSQL已安装
)

echo.
echo ==========================================
echo 开发环境设置完成！
echo ==========================================
echo.
echo 下一步:
echo 1. 激活虚拟环境: venv\Scripts\activate
echo 2. 初始化数据库: python code\scripts\init_databases.py
echo 3. 运行测试: pytest code\tests\
echo 4. 启动服务: python code\scripts\run_all_apis.py

pause
