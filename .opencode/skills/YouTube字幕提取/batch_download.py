#!/usr/bin/env python3
"""
批量下载 YouTube 视频字幕

从文件中读取 YouTube URL 列表，批量下载字幕。

使用示例:
    python batch_download.py --input urls.txt --output-dir ./subtitles
"""

import argparse
import sys
from pathlib import Path
import subprocess


def extract_video_id(url: str) -> str:
    """从 URL 中提取视频 ID"""
    import re

    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    if len(url) == 11:
        return url

    return None


def main():
    parser = argparse.ArgumentParser(
        description="批量下载 YouTube 视频字幕",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从文件读取 URL 列表
  python batch_download.py --input urls.txt --output-dir ./subtitles

  # 指定语言
  python batch_download.py --input urls.txt --output-dir ./subtitles --lang en

URL 文件格式:
  每行一个 YouTube URL，例如:
  https://www.youtube.com/watch?v=VIDEO_ID1
  https://www.youtube.com/watch?v=VIDEO_ID2
  https://youtu.be/VIDEO_ID3
        """,
    )

    parser.add_argument("--input", "-i", required=True, help="包含 YouTube URL 的文件")

    parser.add_argument("--output-dir", "-o", required=True, help="输出目录")

    parser.add_argument("--lang", default="zh,en", help="字幕语言（默认: zh,en）")

    parser.add_argument(
        "--format",
        choices=["markdown", "vtt", "srt"],
        default="markdown",
        help="输出格式（默认: markdown）",
    )

    args = parser.parse_args()

    # 读取 URL 列表
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"❌ 错误: 文件不存在: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print(f"❌ 错误: 未找到有效的 URL", file=sys.stderr)
        sys.exit(1)

    print(f"📋 找到 {len(urls)} 个视频", file=sys.stderr)

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 批量下载
    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls, 1):
        video_id = extract_video_id(url)
        if not video_id:
            print(f"\n[{i}/{len(urls)}] ⏭️  跳过无效 URL: {url}", file=sys.stderr)
            fail_count += 1
            continue

        print(f"\n[{i}/{len(urls)}] 📹 {video_id}", file=sys.stderr)

        # 生成输出文件名
        ext = "md" if args.format == "markdown" else args.format
        output_file = output_dir / f"{video_id}.{ext}"

        if output_file.exists():
            print(f"  ⏭️  跳过 (已存在)", file=sys.stderr)
            continue

        # 调用下载脚本
        cmd = [
            "python",
            Path(__file__).parent / "download_subtitle.py",
            "--url",
            url,
            "--lang",
            args.lang,
            "--format",
            args.format,
            "--output",
            str(output_file),
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=60
            )
            print(f"  ✅ 成功", file=sys.stderr)
            success_count += 1
        except subprocess.TimeoutExpired:
            print(f"  ❌ 超时", file=sys.stderr)
            fail_count += 1
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 失败: {e.stderr}", file=sys.stderr)
            fail_count += 1
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}", file=sys.stderr)
            fail_count += 1

    # 输出统计
    print("\n" + "=" * 60, file=sys.stderr)
    print("批量下载完成！", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"✅ 成功: {success_count}", file=sys.stderr)
    print(f"❌ 失败: {fail_count}", file=sys.stderr)
    print(f"📁 输出目录: {output_dir}", file=sys.stderr)

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
