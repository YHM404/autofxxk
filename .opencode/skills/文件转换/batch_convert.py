#!/usr/bin/env python3
"""
文件批量转换为 Markdown

批量转换目录中的多个文件为 Markdown 格式。

使用示例:
    python batch_convert.py --input-dir ./docs --output-dir ./markdown
    python batch_convert.py --input-dir ./docs --output-dir ./markdown --pattern "*.pdf" --recursive
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List
import fnmatch


def find_files(
    input_dir: Path, pattern: str = "*", recursive: bool = False
) -> List[Path]:
    """查找匹配的文件"""
    files = []

    if recursive:
        for root, _, filenames in os.walk(input_dir):
            for filename in filenames:
                if fnmatch.fnmatch(filename, pattern):
                    files.append(Path(root) / filename)
    else:
        for file_path in input_dir.iterdir():
            if file_path.is_file() and fnmatch.fnmatch(file_path.name, pattern):
                files.append(file_path)

    return sorted(files)


def convert_file(md, input_file: Path, output_file: Path) -> bool:
    """转换单个文件"""
    try:
        result = md.convert(str(input_file))

        # 创建输出目录
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.text_content)

        return True
    except Exception as e:
        print(f"  ❌ 失败: {str(e)}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="批量转换文件为 Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转换目录中的所有文件
  python batch_convert.py --input-dir ./documents --output-dir ./markdown

  # 只转换 PDF 文件
  python batch_convert.py --input-dir ./documents --output-dir ./markdown --pattern "*.pdf"

  # 递归处理子目录
  python batch_convert.py --input-dir ./documents --output-dir ./markdown --recursive

  # 启用插件
  python batch_convert.py --input-dir ./documents --output-dir ./markdown --enable-plugins
        """,
    )

    parser.add_argument("--input-dir", "-i", required=True, help="输入目录路径")

    parser.add_argument("--output-dir", "-o", required=True, help="输出目录路径")

    parser.add_argument(
        "--pattern", "-p", default="*", help="文件匹配模式 (默认: *，即所有文件)"
    )

    parser.add_argument("--recursive", "-r", action="store_true", help="递归处理子目录")

    parser.add_argument("--enable-plugins", action="store_true", help="启用第三方插件")

    parser.add_argument(
        "--azure-endpoint", help="Azure Document Intelligence 端点（可选）"
    )

    parser.add_argument(
        "--skip-existing", action="store_true", help="跳过已存在的输出文件"
    )

    args = parser.parse_args()

    try:
        from markitdown import MarkItDown
    except ImportError:
        print("❌ 错误: 未找到 markitdown 库", file=sys.stderr)
        print("请先运行: bash setup.sh", file=sys.stderr)
        sys.exit(1)

    # 检查输入目录
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"❌ 错误: 输入目录不存在: {input_dir}", file=sys.stderr)
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"❌ 错误: 不是目录: {input_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)

    # 查找文件
    print(f"🔍 查找文件: {args.pattern}", file=sys.stderr)
    if args.recursive:
        print(f"📁 递归搜索: {input_dir}", file=sys.stderr)
    else:
        print(f"📁 搜索目录: {input_dir}", file=sys.stderr)

    files = find_files(input_dir, args.pattern, args.recursive)

    if not files:
        print(f"❌ 未找到匹配的文件", file=sys.stderr)
        sys.exit(1)

    print(f"✓ 找到 {len(files)} 个文件\n", file=sys.stderr)

    # 初始化 MarkItDown
    kwargs = {"enable_plugins": args.enable_plugins}

    if args.azure_endpoint:
        kwargs["docintel_endpoint"] = args.azure_endpoint
        print(
            f"📡 使用 Azure Document Intelligence: {args.azure_endpoint}\n",
            file=sys.stderr,
        )

    md = MarkItDown(**kwargs)

    # 批量转换
    success_count = 0
    skip_count = 0
    fail_count = 0

    for i, input_file in enumerate(files, 1):
        # 计算相对路径
        try:
            rel_path = input_file.relative_to(input_dir)
        except ValueError:
            rel_path = input_file.name

        # 生成输出文件路径（将扩展名改为 .md）
        output_file = output_dir / rel_path.with_suffix(".md")

        print(f"[{i}/{len(files)}] {rel_path}", file=sys.stderr)

        # 检查是否跳过
        if args.skip_existing and output_file.exists():
            print(f"  ⏭️  跳过 (已存在)", file=sys.stderr)
            skip_count += 1
            continue

        # 转换文件
        print(f"  🔄 转换中...", file=sys.stderr)
        if convert_file(md, input_file, output_file):
            print(f"  ✅ 成功 -> {output_file}", file=sys.stderr)
            success_count += 1
        else:
            fail_count += 1

        print()

    # 输出统计
    print("=" * 60, file=sys.stderr)
    print("转换完成！", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"✅ 成功: {success_count}", file=sys.stderr)
    if skip_count > 0:
        print(f"⏭️  跳过: {skip_count}", file=sys.stderr)
    if fail_count > 0:
        print(f"❌ 失败: {fail_count}", file=sys.stderr)
    print(f"📁 输出目录: {output_dir}", file=sys.stderr)

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
