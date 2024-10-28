from pathlib import Path

# Path to the root of the project
ROOT = Path(__file__).parent.parent.parent
SRC_DIR = ROOT / 'src'

# Path to the data directory
ASSETS_DIR = ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
BIN_DIR = ROOT / "bin"
TEMP_DIR = ROOT / "Temp"
OUTPUT_DIR = ROOT / "output"
MODELS_DIR = ROOT / "models"

# FILE
OUTPUT_FILE = ROOT / "output.mp4"
FFMPEG_FILE = BIN_DIR / "ffmpeg.exe"
FFPROBE_FILE = BIN_DIR / "ffprobe.exe"
NOISE_REDUCE_MODEL_FILE = BIN_DIR / "cb.rnnn"  # ffmpeg的降噪模型
CONFIG_FILE = ROOT / "config.json"
LOGO_IMAGE_FILE = IMAGES_DIR / 'logo.ico'
QRC_FILE = ASSETS_DIR / "resource.qrc"
QRC_PY_FILE = ROOT / "resource_rc.py"
LOG_FILE = ROOT / "log.log"
ABOUT_HTML_FILE = ASSETS_DIR / "about.html"
RESUME_FILE = ROOT / "task_resumer.json"
AUDIO_SEPARATOR_EXE_FILE = BIN_DIR / 'audio_sep' / 'audio_sep.exe'

# MODEL
ESPCN_x2_FILE = BIN_DIR / "ESPCN_x2.pb"
LapSRN_x2_FILE = BIN_DIR / "LapSRN_x2.pb"
