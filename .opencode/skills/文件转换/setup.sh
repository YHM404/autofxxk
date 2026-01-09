#!/bin/bash

# 文件转换工具 - 环境设置脚本
# 功能: 创建虚拟环境并安装依赖

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "================================================"
echo "文件转换工具 - 环境设置"
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

# 检查 ffmpeg（音频转录的可选依赖）
echo ""
echo "🔍 检查可选依赖..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n 1 | cut -d' ' -f3)
    echo "✓ 检测到 ffmpeg: $FFMPEG_VERSION"
else
    echo "⚠️  未检测到 ffmpeg (音频转录功能需要)"
    echo "   安装方法:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu: sudo apt-get install ffmpeg"
    echo "   注: 如果不需要音频转录功能，可以忽略此警告"
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
echo "  2. 运行脚本: python convert_file.py --help"
echo "  3. 退出环境: deactivate"
echo ""
echo "支持的文件格式:"
echo "  - 文档: PDF, DOCX, PPTX, XLSX"
echo "  - 图片: JPG, PNG (支持 OCR)"
echo "  - 音频: WAV, MP3 (需要 ffmpeg)"
echo "  - 网页: HTML"
echo "  - 其他: CSV, JSON, XML, ZIP, EPUB"
echo ""
