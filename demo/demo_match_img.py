from assets.sources import get_source
from script_utils.matchTemplate import match_img
import math
import random

from script_utils.loggerConfig import logger


def random_button_coordinate(rectangle):
    """
    随机要点击按钮的坐标
    :return:
    """
    margin = 2
    left_up = rectangle[0]
    right_down = rectangle[3]
    button_width = abs(right_down[0] - left_up[0])
    button_height = abs(right_down[1] - left_up[1])
    min_length = min(button_width, button_height)

    # 按钮的长度或宽度<=3px时,鼠标点击的位置(一般不会有这种情况)
    if min_length - margin * 2 < 3:
        logger.warning("按钮的长度或宽度<=3px,需要精确点击")
        padding = 2
        if button_width - margin * 2 < 3:
            x = (right_down[0] + left_up[0]) / 2
        else:
            num = math.floor(button_width / 3)
            x = random.randint(left_up[0] + num + margin, right_down[0] - num - margin)
        if button_height - margin * 2 < 3:
            y = (right_down[1] + left_up[1]) / 2
        else:
            num = math.floor(button_height / 3)
            y = random.randint(left_up[1] + num + margin, right_down[1] - num - margin)
    else:
        padding = math.floor((button_height - margin * 2) / 3)
        x = random.randint(left_up[0] + padding + margin, right_down[0] - padding - margin)
        y = random.randint(left_up[1] + padding + margin, right_down[1] - padding - margin)

    return x, y, padding


button_name = ["reserves", "reserves_two"]

for name in button_name:
    result = match_img('test6.png', get_source(name), 10, 10, 0.95)[3]
    if result is None:
        print("result is None")
        continue
    rectangle = result['rectangle']
    x, y, padding = random_button_coordinate(rectangle)
    print(f"x:{x},y:{y},padding:{padding}")
    left = rectangle[0][0]
    up = rectangle[0][1]
    right = rectangle[3][0]
    down = rectangle[3][1]

    if left < x + padding < right and left < x - padding < right and up < y + padding < down and up < y - padding < down:
        print("ok!!")
