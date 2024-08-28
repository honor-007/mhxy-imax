import time

import cv2

from assets.sources import get_source
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.components.gameMouse import game_mouse
from src.utils.random_util import random_button_coordinate


def click_button(button_name=None):
    """
    根据sources中的button_name点击对应按钮
    """
    if button_name is None or button_name == "":
        return False
    result = match_img('test13.png', get_source(button_name), 10, 10, 0.95)[3]
    print(f"按钮点击result:{result}")
    if result is not None:
        # 随机按钮上的一个坐标
        x, y, padding = random_button_coordinate(result['rectangle'])
        # x, y = result['result']
        logger.info(f"尝试点击[{button_name}]按钮,x:{x},y:{y},bias:{padding}")
        game_mouse.move_click(x=x, y=y, bias=padding)
        logger.warning(f"点击按钮:{button_name}成功")
        return True
    else:
        # cv2.imwrite("false.png", 'test11.png')
        logger.warning(f"点击按钮:{button_name}失败")
        return False

time.sleep(5)
click_button('escort_3')