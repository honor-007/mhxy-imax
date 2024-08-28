import cv2

from assets.sources import get_source
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.components.gameMouse import start_point
from src.utils.globalVariable import mouse_stop_event


def get_mouse_point(method=cv2.TM_CCORR_NORMED):
    """
    获取计算出来的坐标，(包含截图顶部)
    :param retry:尝试最大次数
    :return: 矩形左上角坐标，即鼠标点点的坐标
    """
    __screenshot = cv2.imread("mouse.png")
    result = match_img(__screenshot, get_source("mouse_template"), 10, 10, 0.98, mask=None, method=method)

    if result[3] is None:
        logger.warning("未能识别出游戏鼠标")
        return 0, 0
    else:
        x, y = result[3]['rectangle'][0]
        # logger.info(f"识别出游戏鼠标,坐标位置({x - 8},{y - 8})")
        return x, y

x,y =get_mouse_point()
print(f"x:{x},y:{y}")