#!/bin/bash

# 金融数据获取 Skill - 环境设置脚本
# 此脚本确保 Python 虚拟环境已创建并安装所有依赖

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "🔧 开始设置金融数据获取环境..."

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3。请先安装 Python 3.8 或更高版本。"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ 找到 Python $PYTHON_VERSION"

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip --quiet

# 安装依赖
echo "📥 安装依赖包..."
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

echo ""
echo "✅ 环境设置完成！"
echo ""
echo "💡 使用说明："
echo "   1. 虚拟环境已激活"
echo "   2. 可以直接运行 Python 脚本，例如："
echo "      python get_stock_data.py --ticker AAPL --period 1y"
echo ""
echo "   要在新的终端会话中使用，请先运行："
echo "   source $VENV_DIR/bin/activate"
echo ""
