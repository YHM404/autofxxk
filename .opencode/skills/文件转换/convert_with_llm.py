#!/usr/bin/env python3
"""
使用 LLM 增强的文件转换

使用 OpenAI 等 LLM 为图片生成详细描述，提升转换质量。
主要用于 PowerPoint 和图片文件。

使用示例:
    python convert_with_llm.py --input image.jpg --api-key YOUR_API_KEY
    python convert_with_llm.py --input presentation.pptx --api-key YOUR_API_KEY --model gpt-4o
"""

import argparse
import sys
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="使用 LLM 增强的文件转换（支持图片详细描述）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转换图片并生成 LLM 描述
  python convert_with_llm.py --input image.jpg --api-key sk-...

  # 转换 PowerPoint（图片将获得详细描述）
  python convert_with_llm.py --input presentation.pptx --api-key sk-... --model gpt-4o

  # 自定义提示词
  python convert_with_llm.py --input image.jpg --api-key sk-... --prompt "详细描述这张图片的内容"

注意:
  - 需要有效的 OpenAI API Key
  - 会产生 API 调用费用
  - 主要用于图片和 PowerPoint 文件
  - 对于纯文档（PDF、Word）等，LLM 增强效果有限
        """,
    )

    parser.add_argument("--input", "-i", required=True, help="输入文件路径")

    parser.add_argument(
        "--output", "-o", help="输出 Markdown 文件路径（不指定则输出到终端）"
    )

    parser.add_argument("--api-key", required=True, help="OpenAI API Key")

    parser.add_argument("--model", default="gpt-4o", help="LLM 模型（默认: gpt-4o）")

    parser.add_argument("--prompt", help="自定义提示词（可选）")

    parser.add_argument(
        "--base-url", help="OpenAI API Base URL（可选，用于自定义端点）"
    )

    args = parser.parse_args()

    try:
        from markitdown import MarkItDown
        from openai import OpenAI
    except ImportError as e:
        print(f"❌ 错误: 缺少依赖库: {str(e)}", file=sys.stderr)
        print("请先运行: bash setup.sh", file=sys.stderr)
        sys.exit(1)

    # 检查输入文件
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"❌ 错误: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 检查文件类型
    file_ext = Path(input_path).suffix.lower()
    supported_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".pptx"]
    if file_ext not in supported_extensions:
        print(f"⚠️  警告: 文件类型 {file_ext} 可能不适合 LLM 增强", file=sys.stderr)
        print(f"建议使用: 图片文件 (.jpg, .png) 或 PowerPoint (.pptx)", file=sys.stderr)
        response = input("是否继续？(y/N): ")
        if response.lower() != "y":
            sys.exit(0)

    # 初始化 OpenAI 客户端
    print("🔄 初始化 OpenAI 客户端...", file=sys.stderr)

    client_kwargs = {"api_key": args.api_key}

    if args.base_url:
        client_kwargs["base_url"] = args.base_url

    try:
        client = OpenAI(**client_kwargs)
    except Exception as e:
        print(f"❌ 错误: 无法初始化 OpenAI 客户端: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # 初始化 MarkItDown with LLM
    print(f"🔄 初始化转换器 (LLM: {args.model})...", file=sys.stderr)

    kwargs = {"llm_client": client, "llm_model": args.model}

    if args.prompt:
        kwargs["llm_prompt"] = args.prompt

    md = MarkItDown(**kwargs)

    # 执行转换
    print(f"📄 正在转换: {input_path}", file=sys.stderr)
    print(f"🤖 使用 LLM 生成图片描述...", file=sys.stderr)

    try:
        result = md.convert(input_path)
        markdown_content = result.text_content

        # 输出结果
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            print(f"✅ 转换成功！", file=sys.stderr)
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
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
