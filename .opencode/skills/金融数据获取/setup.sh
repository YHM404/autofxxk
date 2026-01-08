#!/bin/bash

# 金融数据获取 Skill - 环境设置脚本
# 此脚本确保 Python 虚拟环境已创建并安装所有依赖

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "🔧 开始设置金融数据获取环境..."

# 查找合适的 Python 版本（>= 3.11）
PYTHON_CMD=""
for cmd in python3.13 python3.12 python3.11 python3; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -gt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]); then
            PYTHON_CMD=$cmd
            PYTHON_VERSION=$VERSION
            echo "✅ 找到合适的 Python 版本: $cmd ($VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ 错误: 未找到 Python 3.11 或更高版本"
    echo "   请安装 Python 3.11+ 后重试"
    echo "   提示: 尝试运行 'brew install python@3.12' 或访问 https://www.python.org"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 使用 $PYTHON_CMD 创建虚拟环境..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo "✅ 虚拟环境创建成功 (Python $PYTHON_VERSION)"
else
    echo "✅ 虚拟环境已存在"
    # 验证现有虚拟环境的 Python 版本
    VENV_VERSION=$("$VENV_DIR/bin/python" --version 2>&1 | awk '{print $2}')
    VENV_MAJOR=$(echo $VENV_VERSION | cut -d. -f1)
    VENV_MINOR=$(echo $VENV_VERSION | cut -d. -f2)
    
    if [ "$VENV_MAJOR" -lt 3 ] || ([ "$VENV_MAJOR" -eq 3 ] && [ "$VENV_MINOR" -lt 11 ]); then
        echo "⚠️  警告: 现有虚拟环境 Python 版本为 $VENV_VERSION (< 3.11)"
        echo "   建议删除并重新创建: rm -rf $VENV_DIR"
        exit 1
    fi
    echo "   Python 版本: $VENV_VERSION"
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
