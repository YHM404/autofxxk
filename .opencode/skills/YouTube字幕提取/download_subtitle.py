#!/usr/bin/env python3
"""
YouTube 字幕下载工具

使用 yt-dlp 下载 YouTube 视频字幕并转换为 Markdown。

使用示例:
    python download_subtitle.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
    python download_subtitle.py --url "..." --lang zh --output subtitle.md
"""

import argparse
import sys
import subprocess
import tempfile
import re
from pathlib import Path


def extract_video_id(url: str) -> str:
    """从 URL 中提取视频 ID"""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # 假设直接是 video ID
    if len(url) == 11:
        return url

    return None


def list_subtitles(url: str) -> bool:
    """列出可用的字幕"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-subs", url],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 错误: {e.stderr}", file=sys.stderr)
        return False


def download_subtitle(url: str, lang: str, output_format: str = "vtt") -> Path:
    """下载字幕文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        output_template = str(tmpdir_path / "subtitle")

        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",  # 同时支持自动字幕
            "--sub-lang",
            lang,
            "--skip-download",
            "--sub-format",
            output_format,
            "--output",
            output_template,
            url,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)

            # 查找下载的字幕文件
            subtitle_files = list(tmpdir_path.glob(f"*.{lang}.{output_format}"))
            if not subtitle_files:
                # 尝试查找任何字幕文件
                subtitle_files = list(tmpdir_path.glob(f"*.{output_format}"))

            if not subtitle_files:
                raise FileNotFoundError("未找到下载的字幕文件")

            # 读取内容
            subtitle_path = subtitle_files[0]
            with open(subtitle_path, "r", encoding="utf-8") as f:
                content = f.read()

            return content

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"下载字幕失败: {error_msg}")


def parse_vtt(content: str) -> list:
    """解析 VTT 字幕文件"""
    lines = content.split("\n")
    subtitles = []
    current_time = None
    current_text = []

    for line in lines:
        line = line.strip()

        # 跳过 WEBVTT 头部和空行
        if (
            line.startswith("WEBVTT")
            or line.startswith("Kind:")
            or line.startswith("Language:")
        ):
            continue

        # 时间戳行
        if "-->" in line:
            if current_time and current_text:
                subtitles.append({"time": current_time, "text": " ".join(current_text)})
                current_text = []

            # 提取开始时间
            current_time = line.split("-->")[0].strip()
        elif line and not line.isdigit():
            # 字幕文本
            current_text.append(line)

    # 添加最后一条
    if current_time and current_text:
        subtitles.append({"time": current_time, "text": " ".join(current_text)})

    return subtitles


def convert_to_markdown(subtitles: list, video_id: str = None) -> str:
    """将字幕转换为 Markdown 格式"""
    markdown = "# YouTube 视频字幕\n\n"

    if video_id:
        markdown += f"视频 ID: `{video_id}`\n\n"
        markdown += f"视频链接: https://www.youtube.com/watch?v={video_id}\n\n"

    markdown += f"字幕条数: {len(subtitles)}\n\n"
    markdown += "---\n\n"

    for entry in subtitles:
        time_str = entry["time"]
        text = entry["text"]

        # 转换时间格式 (00:00:48.666 -> 00:48)
        time_parts = time_str.split(":")
        if len(time_parts) >= 2:
            minutes = time_parts[-2]
            seconds = time_parts[-1].split(".")[0]
            time_display = f"{minutes}:{seconds}"
        else:
            time_display = time_str

        markdown += f"**[{time_display}]** {text}\n\n"

    return markdown


def main():
    parser = argparse.ArgumentParser(
        description="下载 YouTube 视频字幕",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 下载字幕并转换为 Markdown
  python download_subtitle.py --url "https://www.youtube.com/watch?v=9JdIkWyyOJI"

  # 指定语言和输出文件
  python download_subtitle.py --url "..." --lang zh --output subtitle.md

  # 列出可用字幕
  python download_subtitle.py --url "..." --list-subs

  # 下载原始 VTT 格式
  python download_subtitle.py --url "..." --format vtt --output subtitle.vtt

支持的语言代码:
  zh - 中文, en - 英文, ja - 日文, ko - 韩文, es - 西班牙文, etc.
        """,
    )

    parser.add_argument("--url", required=True, help="YouTube 视频 URL")

    parser.add_argument(
        "--lang", default="zh,en", help="字幕语言（逗号分隔，默认: zh,en）"
    )

    parser.add_argument("--output", "-o", help="输出文件路径（可选）")

    parser.add_argument(
        "--format",
        choices=["markdown", "vtt", "srt"],
        default="markdown",
        help="输出格式（默认: markdown）",
    )

    parser.add_argument(
        "--list-subs", action="store_true", help="列出所有可用的字幕语言"
    )

    args = parser.parse_args()

    # 提取视频 ID
    video_id = extract_video_id(args.url)
    if not video_id:
        print("❌ 错误: 无法从 URL 中提取视频 ID", file=sys.stderr)
        sys.exit(1)

    print(f"📹 视频 ID: {video_id}", file=sys.stderr)

    # 列出字幕
    if args.list_subs:
        print("\n🔍 查询可用字幕...\n", file=sys.stderr)
        if list_subtitles(args.url):
            sys.exit(0)
        else:
            sys.exit(1)

    # 下载字幕
    languages = [lang.strip() for lang in args.lang.split(",")]
    print(f"🔍 下载字幕 (语言: {', '.join(languages)})...", file=sys.stderr)

    try:
        # 尝试每种语言
        content = None
        used_lang = None

        for lang in languages:
            try:
                print(f"   尝试语言: {lang}...", file=sys.stderr)
                content = download_subtitle(args.url, lang, "vtt")
                used_lang = lang
                break
            except Exception as e:
                print(f"   {lang} 不可用", file=sys.stderr)
                continue

        if not content:
            print("❌ 错误: 未找到任何可用字幕", file=sys.stderr)
            print("提示: 使用 --list-subs 查看可用语言", file=sys.stderr)
            sys.exit(1)

        print(f"✅ 成功下载 {used_lang} 字幕", file=sys.stderr)

        # 处理输出
        if args.format == "markdown":
            subtitles = parse_vtt(content)
            output_content = convert_to_markdown(subtitles, video_id)
            print(f"📊 共 {len(subtitles)} 条字幕", file=sys.stderr)
        else:
            output_content = content

        # 保存或输出
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_content)

            print(f"📝 已保存到: {output_path}", file=sys.stderr)
        else:
            print("\n" + "=" * 60, file=sys.stderr)
            print("字幕内容:", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            print(output_content)

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
