import random

import cv2

from assets.sources import get_source
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.utils.random_util import random_button_coordinate


def click_button(button_name=None):
    """
    根据sources中的button_name点击对应按钮
    """
    screen_shot = cv2.imread('test2.png')

    # img_obj = cv2.imread(get_source(button_name))
    # cv2.imshow("22",img_obj)
    # cv2.waitKey()

    if button_name is None or button_name == "":
        return False
    result = match_img(screen_shot, get_source(button_name), 10, 10, 0.95)[3]
    print(f"按钮点击result:{result}")
    if result is not None:
        # 随机按钮上的一个坐标
        x, y, padding = random_button_coordinate(result['rectangle'])
        # x, y = result['result']
        logger.info(f"尝试点击[{button_name}]按钮,x:{x},y:{y},bias:{padding}")
        # game_mouse.move_click(x=x, y=y, bias=padding)
        logger.info(f"点击按钮:{button_name}成功")
        return True
    else:
        cv2.imwrite("false.png", screen_shot)
        logger.warning(f"点击按钮:{button_name}失败")
        return False


# for i in range(10):
#     click_button('stay_confirm_rest_button')

def stay_dialog():
    screen_shot = cv2.imread('test2.png')
    result = match_img(screen_shot, get_source('stay_dialog'), 10, 10, 0.95)[3]
    left_up = result['rectangle'][0]
    target_x = left_up[0] + random.randint(30, 80)
    target_y = left_up[1] + random.randint(111, 116)
    print(f"target_x:{target_x},target_y:{target_y}")

stay_dialog()