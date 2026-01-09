#!/usr/bin/env python3
"""
将字幕文件转换为 Markdown

支持 VTT 和 SRT 格式。

使用示例:
    python convert_to_markdown.py --input subtitle.vtt --output subtitle.md
"""

import argparse
import sys
import re
from pathlib import Path


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


def parse_srt(content: str) -> list:
    """解析 SRT 字幕文件"""
    lines = content.split("\n")
    subtitles = []
    current_time = None
    current_text = []
    expect_time = False

    for line in lines:
        line = line.strip()

        # 序号行（纯数字）
        if line.isdigit():
            if current_time and current_text:
                subtitles.append({"time": current_time, "text": " ".join(current_text)})
                current_text = []
                current_time = None
            expect_time = True
        # 时间戳行
        elif "-->" in line and expect_time:
            current_time = line.split("-->")[0].strip()
            expect_time = False
        # 字幕文本
        elif line:
            current_text.append(line)

    # 添加最后一条
    if current_time and current_text:
        subtitles.append({"time": current_time, "text": " ".join(current_text)})

    return subtitles


def convert_to_markdown(subtitles: list, title: str = "YouTube 视频字幕") -> str:
    """将字幕转换为 Markdown 格式"""
    markdown = f"# {title}\n\n"
    markdown += f"字幕条数: {len(subtitles)}\n\n"
    markdown += "---\n\n"

    for entry in subtitles:
        time_str = entry["time"]
        text = entry["text"]

        # 转换时间格式 (00:00:48.666 -> 00:48)
        # 处理多种时间格式
        time_match = re.search(r"(\d+):(\d+):(\d+)", time_str)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            seconds = int(time_match.group(3))

            if hours > 0:
                time_display = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                time_display = f"{minutes:02d}:{seconds:02d}"
        else:
            time_display = time_str

        markdown += f"**[{time_display}]** {text}\n\n"

    return markdown


def main():
    parser = argparse.ArgumentParser(
        description="将字幕文件转换为 Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转换 VTT 文件
  python convert_to_markdown.py --input subtitle.vtt --output subtitle.md

  # 转换 SRT 文件
  python convert_to_markdown.py --input subtitle.srt --output subtitle.md

  # 指定标题
  python convert_to_markdown.py --input subtitle.vtt --output subtitle.md --title "视频标题"
        """,
    )

    parser.add_argument("--input", "-i", required=True, help="输入字幕文件路径")

    parser.add_argument("--output", "-o", help="输出 Markdown 文件路径（可选）")

    parser.add_argument("--title", default="YouTube 视频字幕", help="Markdown 标题")

    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 错误: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 根据文件类型解析
    file_ext = input_path.suffix.lower()
    print(f"📄 解析 {file_ext} 文件...", file=sys.stderr)

    if file_ext == ".vtt":
        subtitles = parse_vtt(content)
    elif file_ext == ".srt":
        subtitles = parse_srt(content)
    else:
        # 尝试自动检测
        if "WEBVTT" in content:
            print("   检测为 VTT 格式", file=sys.stderr)
            subtitles = parse_vtt(content)
        elif "-->" in content and content.split("\n")[0].isdigit():
            print("   检测为 SRT 格式", file=sys.stderr)
            subtitles = parse_srt(content)
        else:
            print("❌ 错误: 无法识别文件格式", file=sys.stderr)
            sys.exit(1)

    if not subtitles:
        print("❌ 错误: 未找到任何字幕", file=sys.stderr)
        sys.exit(1)

    print(f"✅ 解析成功，共 {len(subtitles)} 条字幕", file=sys.stderr)

    # 转换为 Markdown
    markdown_content = convert_to_markdown(subtitles, args.title)

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"📝 已保存到: {output_path}", file=sys.stderr)
    else:
        print("\n" + "=" * 60, file=sys.stderr)
        print("Markdown 内容:", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        print(markdown_content)


if __name__ == "__main__":
    main()
