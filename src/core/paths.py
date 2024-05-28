from pathlib import Path

# Path to the root of the project
ROOT = Path(__file__).parent.parent.parent
SRC_DIR = ROOT / 'src'

# Path to the data directory
ASSETS_DIR = ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
BIN_DIR = ROOT / "bin"
TEMP_DIR = ROOT / "Temp"

# FILE
OUTPUT_FILE = ROOT / "output.mp4"
FFMPEG_FILE = BIN_DIR / "ffmpeg.exe"
CONFIG_FILE = ROOT / "config.json"
LOGO_IMAGE_FILE = IMAGES_DIR / 'logo.ico'
QRC_FILE = ASSETS_DIR / "resource.qrc"
QRC_PY_FILE = ROOT / "resource_rc.py"
LOG_FILE = ROOT / "log.log"
