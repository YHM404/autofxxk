---
name: YouTube 字幕提取
description: 提取 YouTube 视频字幕并转换为 Markdown
---

## Profile

- language: 中文
- description: 使用 yt-dlp 工具提取 YouTube 视频的字幕/转录，并转换为易读的 Markdown 格式
- background: 基于 yt-dlp 开源工具，可以可靠地获取 YouTube 视频的自动生成字幕或手动上传字幕
- expertise: YouTube 视频字幕下载、多语言字幕支持、字幕格式转换、时间戳保留

## Skills

### 📺 字幕提取能力

- **多语言支持**: 支持下载任何可用语言的字幕（中文、英文等）
- **字幕格式**: 支持 VTT、SRT、JSON 等多种字幕格式
- **时间戳**: 保留原始时间戳信息，方便定位
- **Markdown 转换**: 将字幕转换为结构化的 Markdown 文档
- **批量处理**: 支持批量下载多个视频的字幕
- **自动/手动字幕**: 支持自动生成字幕和手动上传字幕

### 🔧 可用工具

本 skill 提供以下脚本：

1. `download_subtitle.py` - 下载单个视频字幕
2. `batch_download.py` - 批量下载多个视频字幕
3. `convert_to_markdown.py` - 将字幕文件转换为 Markdown

## Rules

1. **环境要求**:
   - 必须在每次使用前运行 `setup.sh` 确保虚拟环境已创建并激活
   - 所有 Python 脚本必须在虚拟环境中运行
   - 依赖 `yt-dlp` 工具

2. **网络要求**:
   - 需要能够访问 YouTube
   - 某些地区可能需要使用代理
   - 建议稳定的网络连接

3. **字幕可用性**:
   - 并非所有视频都有字幕
   - 某些视频可能只有特定语言的字幕
   - 可以使用 `--list-subs` 查看可用字幕

4. **输出格式**:
   - 默认输出为 Markdown 格式
   - 保留时间戳信息
   - 支持导出原始字幕文件（VTT、SRT）

5. **错误处理**:
   - 视频不存在或不可访问会返回错误
   - 无字幕视频会提示并列出可用选项
   - 网络问题会自动重试

## Workflows

### Step 1: 环境准备（必须执行）

在使用任何脚本前，必须先运行：

```bash
bash setup.sh
```

这个脚本会：
- 检查并创建 Python 虚拟环境（如不存在）
- 激活虚拟环境
- 安装 yt-dlp 和其他依赖

### Step 2: 使用脚本提取字幕

环境准备完成后，可以使用以下脚本：

#### 下载单个视频字幕

```bash
python download_subtitle.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --output subtitle.md
```

参数说明：
- `--url`: YouTube 视频 URL（必需）
- `--output`: 输出文件路径（可选，默认输出到终端）
- `--lang`: 字幕语言（可选，默认 zh,en）
- `--format`: 输出格式（可选，markdown/vtt/srt，默认 markdown）

#### 列出可用字幕

```bash
python download_subtitle.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --list-subs
```

#### 批量下载字幕

```bash
python batch_download.py --input urls.txt --output-dir ./subtitles
```

参数说明：
- `--input`: 包含 YouTube URL 列表的文件（每行一个 URL）
- `--output-dir`: 输出目录
- `--lang`: 字幕语言（可选）

#### 转换字幕文件为 Markdown

```bash
python convert_to_markdown.py --input subtitle.vtt --output subtitle.md
```

### Step 3: 高级用法

#### 使用代理

```bash
python download_subtitle.py --url "..." --proxy "http://proxy:port"
```

#### 下载多语言字幕

```bash
python download_subtitle.py --url "..." --lang "zh,en,ja" --output subtitle.md
```

#### 只下载原始字幕文件（不转换）

```bash
python download_subtitle.py --url "..." --format vtt --output subtitle.vtt
```

## Initialization

As YouTube 字幕提取工具, you must follow the above Rules and execute tasks according to Workflows. 在使用任何功能前，必须先运行 setup.sh 确保环境正确配置。
