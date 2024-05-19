import subprocess
from concurrent.futures import ThreadPoolExecutor

from src.core.paths import ASSETS_DIR, SRC_DIR

UI_DIR = ASSETS_DIR / "ui"
PY_DIR = SRC_DIR / "interface"

count = 0
thread_pool = ThreadPoolExecutor(10)

print("正在清空Ui_*.py文件夹下的所有内容")
# 清空Ui_*.py文件夹下的所有内容
for each in PY_DIR.glob("**/*.*"):
    if each.stem.startswith("Ui_"):
        print(f"正在删除{each}……")
        each.unlink()


def trans_ui_to_py(ui_file):
    print(f"当前正在转换{ui_file}……")
    py_file = PY_DIR / f"Ui_{ui_file.stem}.py"
    subprocess.run(["pyside6-uic", ui_file, "-o", py_file])


for ui_file in UI_DIR.glob("**/*.ui"):
    count += 1
    thread_pool.submit(trans_ui_to_py, ui_file)

thread_pool.shutdown(wait=True)

print(f"Done! {count} files have been converted.")
