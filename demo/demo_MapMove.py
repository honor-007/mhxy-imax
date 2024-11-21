import random
import time

import cv2
import win32gui

from assets.sources import proxies_data, get_source, write_json
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.components.InputAutoGui import inputautogui
from src.components.gameMouse import game_mouse
from src.components.window import get_window, WINDOW_ID
from src.modules.map import get_yellow_text

def __screenshot():
    print(f"WINDOW_ID:{WINDOW_ID}")
    return winShot(WINDOW_ID)
def MapMove(x, y, region, next=None):
    """
        OCR 得方法去移动点击小地图上点，在线程中每次加载会很慢
        :param x: tab地图上传送点x坐标
        :param y: tab地图上传送点y坐标
        :param region: 当前场景
        :param next: 当前场景要去的下个场景
        :return:

        """
    # log_queue.put(f"场景移动{region}->{next},小地图坐标点击({x},{y})")
    if region in ["轮回司"]:
        return
    inputautogui.press('tab')
    # if next in ["狮驼岭"]:
    #     self.__close_exit_box()
    # Mouse().move(600, 550)
    if region in proxies_data:
        dx = proxies_data[region]['dx']
        dy = proxies_data[region]['dy']
        if 'start_point' in proxies_data[region]:
            start = proxies_data[region]['start_point'][0]
            bias_x = proxies_data[region]['start_point'][1]
            bias_y = proxies_data[region]['start_point'][2]

            result = match_img(__screenshot(), get_source('map_flag'), 10, 10, 0.95)[3]
            if result is None:
                return
            map_xy = result['result']
            x1, y1 = start[0], start[1]
            x2, y2 = map_xy[0] + bias_x, map_xy[1] + bias_y
            target_x = (x - x1) * dx + x2
            target_y = (y - y1) * dy + y2
        else:
            xs = random.randint(490, 510)
            ys = random.randint(340, 360)
            game_mouse.client_move(xs, ys)
            time.sleep(1)
            (x1, y1), (x2, y2) = get_yellow_text()
            if x1 == 0 and x2 == 0:
                return
            start = (x1, y1)
            result = match_img(__screenshot(), get_source('map_flag'), 10, 10, 0.95)[3]
            if result is None:
                print("未找到小地图标识")
                return
            map_xy = result['result']
            bias_x = x2 - map_xy[0]
            bias_y = y2 - map_xy[1]
            proxies_data.update({region: {'start_point': [start, bias_x, bias_y], 'dx': dx, 'dy': dy}})
            write_json(proxies_data, 'proxies')
            target_x = (x - x1) * dx + x2
            target_y = (y - y1) * dy + y2

    else:
        xs = random.randint(490, 510)
        ys = random.randint(340, 360)
        game_mouse.locked_client_move(xs, ys)
        time.sleep(1)
        print("正在记录地图比例尺")
        (x1, y1), (x2, y2) = get_yellow_text()
        if x1 == 0:
            return
        dddd = 100
        yyyy = 100
        game_mouse.move(x2 + dddd, y2 + yyyy, bias=0)
        time.sleep(2)
        (x3, y3), (x4, y4) = get_yellow_text()
        if x3 == 0:
            return
        dx = dddd / abs(x1 - x3)
        dy = -yyyy / abs(y1 - y3)
        proxies_data.update({region: {'dx': dx, 'dy': dy}})
        target_x = (x - x3) * dx + x4
        target_y = (y - y3) * dy + y4
        write_json(proxies_data, 'proxies')
        print("{}地图比例尺记录结束,dx:{},dy:{}".format(region, dx, dy))
    print(f"当前场景移动,{region}->{next},小地图坐标({x},{y}),游戏鼠标坐标({round(target_x)},{round(target_y)})")
    game_mouse.move_click(round(target_x), round(target_y), bias=2)
    time.sleep(1)
    inputautogui.press('tab')

    return 1
    pass


# time.sleep(2)
# shot = winShot(WINDOW_ID)
# cv2.imshow("22",shot)
# cv2.waitKey()
# MapMove(280, 40, '长安城', '大唐国境-驿站')
