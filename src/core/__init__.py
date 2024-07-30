from typing_extensions import Final

# 所有支持的视频文件后缀名
AVAILABLE_VIDEO_SUFFIX: Final[list[str]] = [
        '.avi',  # Audio Video Interleave
        '.mp4',  # MPEG-4 Part 14
        '.mov',  # QuickTime File Format
        '.mkv',  # Matroska
        '.flv',  # Flash Video
        '.wmv',  # Windows Media Video
        '.mpeg',  # MPEG Video
        '.mpg',  # MPEG Video
        '.m4v',  # MPEG-4 Video
        '.3gp',  # 3GPP Multimedia File
        '.webm'  # WebM Video
        ]

# 包含这些关键词的FFmpeg输出信息会被认为是错误信息
FFMPEG_ERROR_WORDS: Final[list[str]] = [
        'error',
        'fail',
        'not',
        'invalid',
        'unknown'
        ]

# 最新的项目下载地址
LATEST_RELEASE_URL: Final[str] = "https://github.com/271374667/VideoFusion/releases/latest"
