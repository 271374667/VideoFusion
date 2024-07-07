import argparse
from pathlib import Path

import loguru

from src.core.enums import Orientation

description = """批量视频处理工具
目前更加细致的设定请前往GUI中进行设置,命令只提供最基础的合并功能
"""

parser = argparse.ArgumentParser(description=description)
parser.add_argument('-i', '--input', type=str, help='包含视频文件地址的txt文件的地址')
parser.add_argument("--video_oritation", type=str, default='horization', choices=['vertical', 'horization'],
                    help='视频的方向')


def parse_args():
    # 解析视频文件地址
    input_txt_path: Path = Path(parser.parse_args().input)
    video_path_list: list[Path] = []
    if not input_txt_path.exists():
        loguru.logger.error(f'txt文件{input_txt_path}不存在')
        raise FileNotFoundError(f'txt文件{input_txt_path}不存在')

    # 判断里面每一行是否都是路径
    for line in input_txt_path.read_text().replace('"', '').splitlines():
        real_path = Path(line)
        if not real_path.exists():
            loguru.logger.error(f'视频文件{line}不存在,请检查txt文件中的路径是否正确')
            raise FileNotFoundError(f'视频文件{line}不存在,请检查txt文件中的路径是否正确')
        video_path_list.append(real_path)

    loguru.logger.debug(f'一共加载了{len(video_path_list)}个视频文件,分别是{video_path_list}')

    # 解析视频朝向
    video_orientation = parser.parse_args().video_oritation
    if video_orientation == 'vertical':
        video_orientation = Orientation.VERTICAL
    else:
        video_orientation = Orientation.HORIZONTAL
    loguru.logger.debug(f'视频的方向为{video_orientation}')


if __name__ == '__main__':
    parse_args()
    print(parser.print_help())
    print(parser.parse_args())
