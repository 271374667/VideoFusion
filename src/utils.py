import time
from functools import wraps

import loguru


def singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def timit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        loguru.logger.debug(f"\n{func.__name__}执行时间:{end_time - start_time}\n")
        return result

    return wrapper


def calculate_dimensions(width: int, height: int, target_width: int, target_height: int):
    if width == 0 or height == 0:
        loguru.logger.critical("视频的宽度或高度为0, 请检查视频")
        raise ValueError("Width or height is 0")
    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    pad_top = (target_height - new_height) // 2
    pad_bottom = target_height - new_height - pad_top
    pad_left = (target_width - new_width) // 2
    pad_right = target_width - new_width - pad_left
    return new_width, new_height, pad_top, pad_bottom, pad_left, pad_right


def evenly_distribute_numbers(current_num: int, target_num: int) -> list[int]:
    """平滑抽帧"""
    if current_num <= target_num:
        raise ValueError("current_num must be greater than target_num")

    diff = current_num - target_num  # 需要移除的数字个数
    interval = current_num / diff  # 平均间隔

    # 生成初始列表
    numbers = list(range(1, current_num + 1))

    # 移除均匀间隔位置的数字
    for i in range(diff):
        remove_index = int(round(i * interval))
        if remove_index < len(numbers):
            numbers.pop(remove_index)

    return numbers


def evenly_interpolate_numbers(current_num: int, target_num: int) -> list[int]:
    """平滑插值"""
    if current_num >= target_num:
        raise ValueError("current_num must be less than target_num")

    diff = target_num - current_num  # 需要增加的数字个数
    interval = (current_num - 1) / (diff + 1)  # 插入位置的平均间隔

    # 生成初始列表
    numbers = list(range(1, current_num + 1))
    new_numbers = []

    # 均匀插入数字
    insert_count = 0
    for i in range(current_num):
        new_numbers.append(numbers[i])
        # 计算插入点
        while insert_count < diff and (i + 1) >= round((insert_count + 1) * interval):
            new_numbers.append(numbers[i])
            insert_count += 1

    return new_numbers


if __name__ == '__main__':
    # 抽帧示例用法
    # current_num = 180000
    # target_num = 150000
    # result = evenly_distribute_numbers(current_num, target_num)
    # print(f"抽帧:{result}")
    # print(len(result))

    # 插帧示例用法
    current_num = 20
    target_num = 30
    result = evenly_interpolate_numbers(current_num, target_num)
    print(f"插帧:{result}")
