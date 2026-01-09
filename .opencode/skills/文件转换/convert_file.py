#!/usr/bin/env python3
"""
文件转换为 Markdown - 单文件转换工具

使用 Microsoft MarkItDown 将各种文件格式转换为 Markdown。

支持格式:
- PDF, DOCX, PPTX, XLSX, XLS
- 图片 (JPG, PNG, GIF) - 支持 OCR
- 音频 (WAV, MP3) - 支持转录
- HTML, CSV, JSON, XML
- ZIP, EPUB
- YouTube URL

使用示例:
    python convert_file.py --input document.pdf --output output.md
    python convert_file.py --input image.jpg
    python convert_file.py --input "https://youtube.com/watch?v=..."
"""

import argparse
import sys
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="将各种文件格式转换为 Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的文件格式:
  文档: PDF, DOCX, PPTX, XLSX, XLS
  图片: JPG, PNG, GIF (支持 OCR)
  音频: WAV, MP3 (支持转录)
  网页: HTML
  数据: CSV, JSON, XML
  其他: ZIP, EPUB
  在线: YouTube URL

使用示例:
  # 转换 PDF 文件
  python convert_file.py --input document.pdf --output output.md

  # 转换图片（自动 OCR）
  python convert_file.py --input image.jpg

  # 转换 YouTube 视频（获取转录）
  python convert_file.py --input "https://www.youtube.com/watch?v=VIDEO_ID"

  # 启用插件
  python convert_file.py --input file.pdf --enable-plugins

  # 使用 Azure Document Intelligence
  python convert_file.py --input file.pdf --azure-endpoint YOUR_ENDPOINT
        """,
    )

    parser.add_argument("--input", "-i", required=True, help="输入文件路径或 URL")

    parser.add_argument(
        "--output", "-o", help="输出 Markdown 文件路径（不指定则输出到终端）"
    )

    parser.add_argument("--enable-plugins", action="store_true", help="启用第三方插件")

    parser.add_argument(
        "--azure-endpoint",
        help="Azure Document Intelligence 端点（可选，用于高质量文档转换）",
    )

    parser.add_argument("--list-plugins", action="store_true", help="列出已安装的插件")

    args = parser.parse_args()

    try:
        from markitdown import MarkItDown
    except ImportError:
        print("❌ 错误: 未找到 markitdown 库", file=sys.stderr)
        print("请先运行: bash setup.sh", file=sys.stderr)
        sys.exit(1)

    # 列出插件
    if args.list_plugins:
        print("📦 查询已安装的插件...")
        print("使用命令: markitdown --list-plugins")
        os.system("markitdown --list-plugins")
        return

    # 检查输入文件
    input_path = args.input
    if not input_path.startswith("http"):  # 不是 URL
        if not os.path.exists(input_path):
            print(f"❌ 错误: 文件不存在: {input_path}", file=sys.stderr)
            sys.exit(1)

    # 初始化 MarkItDown
    print("🔄 初始化转换器...", file=sys.stderr)

    kwargs = {"enable_plugins": args.enable_plugins}

    if args.azure_endpoint:
        kwargs["docintel_endpoint"] = args.azure_endpoint
        print(
            f"📡 使用 Azure Document Intelligence: {args.azure_endpoint}",
            file=sys.stderr,
        )

    md = MarkItDown(**kwargs)

    # 执行转换
    print(f"📄 正在转换: {input_path}", file=sys.stderr)

    try:
        result = md.convert(input_path)
        markdown_content = result.text_content

        # 输出结果
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            print("✅ 转换成功！", file=sys.stderr)
            print(f"📝 输出文件: {output_path}", file=sys.stderr)
            print(f"📊 内容长度: {len(markdown_content)} 字符", file=sys.stderr)
        else:
            # 输出到终端
            print("\n" + "=" * 60, file=sys.stderr)
            print("转换结果:", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            print(markdown_content)
            print("\n" + "=" * 60, file=sys.stderr)
            print(f"📊 内容长度: {len(markdown_content)} 字符", file=sys.stderr)

    except Exception as e:
        print(f"❌ 转换失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
