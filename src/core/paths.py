from pathlib import Path

# Path to the root of the project
ROOT = Path(__file__).parent.parent.parent
SRC_DIR = ROOT / 'src'

# Path to the data directory
ASSETS_DIR = ROOT / "assets"
BIN_DIR = ROOT / "bin"
TEMP_DIR = Path(r'D:\Temp')

# FILE
OUTPUT_FILE = ROOT / "output.mp4"
FFMPEG_FILE = BIN_DIR / "ffmpeg.exe"
CONFIG_FILE = ROOT / "config.json"
