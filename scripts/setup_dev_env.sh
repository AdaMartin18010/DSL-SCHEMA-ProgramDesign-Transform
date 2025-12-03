#!/bin/bash
# 开发环境设置脚本

set -e

echo "=========================================="
echo "DSL Schema项目 - 开发环境设置"
echo "=========================================="

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装Python依赖
echo "安装Python依赖..."
pip install --upgrade pip
pip install -r code/requirements.txt

# 安装TypeScript依赖
if [ -f "code/package.json" ]; then
    echo "安装TypeScript依赖..."
    cd code
    npm install
    cd ..
fi

# 检查PostgreSQL
echo "检查PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "PostgreSQL已安装"
else
    echo "警告: PostgreSQL未安装，请手动安装"
fi

# 检查pgvector扩展
echo "检查pgvector扩展..."
if psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name='vector';" &> /dev/null; then
    echo "pgvector扩展可用"
else
    echo "警告: pgvector扩展未安装，请手动安装"
fi

echo ""
echo "=========================================="
echo "开发环境设置完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 初始化数据库: make init-db"
echo "3. 运行测试: make test"
echo "4. 启动服务: make start"
