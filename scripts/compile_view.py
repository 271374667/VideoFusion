import subprocess
from concurrent.futures import ThreadPoolExecutor

from src.core.paths import ASSETS_DIR, SRC_DIR, QRC_FILE, QRC_PY_FILE

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

print("正在替换资源文件")
for each in PY_DIR.glob("**/*.py"):
    if each.stem == "__init__":
        continue

    with open(each, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("import res_rc", "from src.resource import rc_res")
    with open(each, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"替换{each}的 res 路径成功!")

print(f"Done! {count} files have been converted.")

# 替换qrc文件
print("正在编译资源文件")
# 使用 pyside6-rcc 命令将 qrc 文件编译成 py 文件
subprocess.run(["pyside6-rcc", str(QRC_FILE), "-o", str(QRC_PY_FILE)])
print("编译完成")
