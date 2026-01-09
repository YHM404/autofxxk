#!/bin/bash

# YouTube 字幕提取工具 - 环境设置脚本
# 功能: 创建虚拟环境并安装依赖

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "================================================"
echo "YouTube 字幕提取工具 - 环境设置"
echo "================================================"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    echo "请先安装 Python 3.10 或更高版本"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ 检测到 Python 版本: $PYTHON_VERSION"

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✓ 虚拟环境创建成功"
else
    echo "✓ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip --quiet

# 安装依赖
echo "📦 安装依赖包..."
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet

if [ $? -eq 0 ]; then
    echo "✓ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 检查 yt-dlp 是否正常
echo ""
echo "🔍 验证 yt-dlp..."
if command -v yt-dlp &> /dev/null; then
    YT_DLP_VERSION=$(yt-dlp --version)
    echo "✓ yt-dlp 版本: $YT_DLP_VERSION"
else
    echo "❌ yt-dlp 未正确安装"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ 环境设置完成！"
echo "================================================"
echo ""
echo "虚拟环境路径: $VENV_DIR"
echo ""
echo "使用方法:"
echo "  1. 激活虚拟环境: source $VENV_DIR/bin/activate"
echo "  2. 运行脚本: python download_subtitle.py --help"
echo "  3. 退出环境: deactivate"
echo ""
echo "功能特性:"
echo "  - 支持多语言字幕下载"
echo "  - 自动转换为 Markdown 格式"
echo "  - 保留时间戳信息"
echo "  - 支持批量处理"
echo ""
echo "示例:"
echo "  python download_subtitle.py --url 'https://youtube.com/watch?v=...' --output subtitle.md"
echo ""
