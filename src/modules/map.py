import random
import time

import cv2
import win32gui

from assets.sources import location_data, get_source, proxies_data, write_json, join_path, location_name_supplement_data
from script_utils.cnOcr import cn_ocr, get_closed_string, get_chinese_text, get_number
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterLocationWhite, hsvFilterErrorYellow
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import crop_image_data, match_img
from script_utils.pathSearch import path_search
from src.components.status import isFight, isMoved
from src.components.InputAutoGui import inputautogui
from src.components.window import WINDOW_ID, set_parent_foreground
from src.components.gameMouse import game_mouse
from src.utils.random_util import random_button_coordinate
from src.utils.globalVariable import task_stop_event, log_queue, module_task_stop_event


def click_button(button_name=None):
    """
    根据sources中的button_name点击对应按钮
    """
    if button_name is None or button_name == "":
        return False
    result = match_img(winShot(WINDOW_ID), get_source(button_name), 10, 10, 0.95)[3]
    print(f"按钮点击result:{result}")
    if result is not None:
        # 随机按钮上的一个坐标
        x, y, padding = random_button_coordinate(result['rectangle'])
        # x, y = result['result']
        logger.info(f"尝试点击[{button_name}]按钮,x:{x},y:{y},bias:{padding}")
        game_mouse.move_click(x=x, y=y, bias=padding)
        logger.info(f"点击按钮:{button_name}成功")
        return True
    else:
        cv2.imwrite("false.png", winShot(WINDOW_ID))
        logger.warning(f"点击按钮:{button_name}失败")
        return False


def click_button_v2(button_image_name):
    """
    move文件夹下的按钮
    """
    if button_image_name is None or button_image_name == "":
        return False
    result = match_img(winShot(WINDOW_ID), join_path('move', button_image_name), 10, 10, 0.95)[3]
    if result is not None:
        x, y = result['result']
        game_mouse.move_click(x, y)
        return True
    return False


def click_transport_npc(now, target):
    """
    点击传送npc
    :param now: 当前地图
    :param target: 目的地图
    :return:
    """
    action = location_data[now][target]["action"]
    if "template" and "mask" in action:
        mask_name = action["mask"]
        template = join_path('move', action["template"])
        if mask_name is not None:
            mask = join_path('move', mask_name)
            result = match_img(winShot(WINDOW_ID), template, 10, 10, 0.92, mask)[3]
            if result is not None:
                x, y = result['result']
                x, y = x, y - 70
                game_mouse.move_click(x, y)
                time.sleep(1)
                return True, (x, y)
        else:
            result = match_img(winShot(WINDOW_ID), template, 10, 10, 0.92)[3]
            if result is not None:
                x, y = result['result']
                x, y = x, y
                game_mouse.move_click(x, y)
                time.sleep(1)
                return True, (x, y)
    return False, (None, None)


def get_yellow_text() -> [(int, int), (int, int)]:
    x, y = game_mouse.get_mouse_point()
    corp = crop_image_data(winShot(WINDOW_ID), (x - 38, y - 28),
                           (x + 46, y - 8))
    re = hsvFilterErrorYellow(corp)
    raw = cn_ocr.ocr_for_single_line(re)
    number_list = get_number(raw)
    if len(number_list) < 2:
        return [(0, 0), (x, y)]
    return [(int(number_list[0]), int(number_list[1])), (x, y)]


class Map:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def __if_windows_in_screen(self) -> bool:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd)

    def __close_exit_box(self):
        """
            取消选择地图上的出口单选框
        """
        result_1 = match_img(self.__screenshot(), get_source('map_exit_flag'), 10, 10, 0.99)[3]
        result_2 = match_img(self.__screenshot(), get_source('map_exit_flag_2'), 10, 10, 0.99)[3]
        if result_1 is not None:
            x, y = result_1['result']
            game_mouse.move_click(x, y)
            return
        if result_2 is not None:
            x, y = result_2['result']
            game_mouse.move_click(x, y)
            return

    def GetMapName(self) -> str:
        screenshot = self.__screenshot()
        img = crop_image_data(screenshot, left_up=(18, 24),
                              right_down=(140, 42))
        raw_text = cn_ocr.ocr_for_single_line(hsvFilterLocationWhite(img, mask=True))['text']
        chinese_text = get_chinese_text(raw_text)
        location_name_list = [location for location in location_data.keys()] + [location for location in
                                                                                location_name_supplement_data]
        return get_closed_string(chinese_text, location_name_list)

    def __is_map_open(self) -> bool:
        screenshot = self.__screenshot()
        result = match_img(screenshot, get_source('map_flag'), 10, 10, 0.95)
        if result[3] is not None:
            return True
        return False

    def openMap(self, retry=2):
        retry_time = retry
        while True:
            if retry_time <= 0:
                break
            if self.__if_windows_in_screen():
                if self.__is_map_open():
                    logger.info("小地图已经开")
                    break
                else:
                    logger.info("小地图已经关闭，正在打开")
                    inputautogui.press('tab')
                    time.sleep(0.1)
            else:
                logger.info("梦幻不在当前窗口")
                set_parent_foreground(self.hwnd)
                time.sleep(2)
                retry_time -= 1
        return

    def MapMove(self, x, y, region, next=None):
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
        self.openMap()
        logger.info("开始进行地图点击")
        if next in ["狮驼岭"]:
            self.__close_exit_box()
        # Mouse().move(600, 550)
        if region in proxies_data:
            dx = proxies_data[region]['dx']
            dy = proxies_data[region]['dy']
            if 'start_point' in proxies_data[region]:
                start = proxies_data[region]['start_point'][0]
                bias_x = proxies_data[region]['start_point'][1]
                bias_y = proxies_data[region]['start_point'][2]

                result = match_img(self.__screenshot(), get_source('map_flag'), 10, 10, 0.95)[3]
                if result is None:
                    logger.info("未找到小地图标识")
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
                result = match_img(self.__screenshot(), get_source('map_flag'), 10, 10, 0.95)[3]
                if result is None:
                    logger.info("未找到小地图标识")
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
            logger.info("正在记录地图比例尺")
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
            logger.info("{}地图比例尺记录结束,dx:{},dy:{}".format(region, dx, dy))
        logger.info(
            f"当前场景移动,{region}->{next},小地图坐标({x},{y}),游戏鼠标坐标({round(target_x)},{round(target_y)})")
        game_mouse.move_click(round(target_x), round(target_y), bias=2)
        time.sleep(1)
        inputautogui.press('tab')

        return 1
        pass

    def MoveToTarget(self, end, name):
        """
        移动到目的地
        :param end: 目的地
        :param name:
        :return:
        """
        log_queue.put(f"开始向目的地图场景[{end}]移动")
        # 是否停止移动
        if name == '':
            return
        # 到达目的场景，移动
        previous_city = ''  # 上一个场景
        while True:
            if task_stop_event.is_set():
                return

            while isFight.is_fighting():
                logger.info("战斗中，等待战斗结束")
                time.sleep(1)
            now_city = self.GetMapName()

            if now_city == end:
                logger.info("已到达目的地，退出自动寻路")
                break

            if task_stop_event.is_set():
                return

            # 有没有需要点击的东西
            if previous_city == now_city:
                if click_button('yes_i_will_go'):
                    now_city = self.GetMapName()
                # 有没有干扰项目
                else:
                    click_button('close_button_x')

            previous_city = now_city
            path = path_search.a_star_algorithm(now_city, end)
            log_queue.put(f"当前场景:{now_city},目的场景{end},计算路线:{path}")
            if path is None:
                logger.warning(f"无法查到从当前场景:{now_city}到目的场景{end}的路线")
                return

            next_city = path[1]

            # 地图上传送点坐标
            info = location_data[now_city][next_city]
            x, y = info["XY"]

            # 3 代表当前场景不能打开地图,需要执行一连串的鼠标点击来进入next_city场景
            if info["action"]["type"] == 3:
                xy_list = info["action"]["xy"]
                for xy in xy_list:
                    x, y = xy
                    # 停止节点
                    if task_stop_event.is_set():
                        return
                    # 增加随机，避免一直点一个点
                    game_mouse.move_click(x, y, bias=10)
                    click_times = random.randrange(0, 3, 1)
                    while click_times > 0:
                        # 停止节点
                        if task_stop_event.is_set():
                            return
                        game_mouse.left_click()
                        click_times -= 1
                    time.sleep(random.uniform(3, 4))
                    map_name = self.GetMapName()
                    if map_name == next_city:
                        break
                continue

            # tab打开地图并移动到传送点
            s = self.MapMove(x, y, now_city, next=next_city)

            if s is None:
                continue

            log_queue.put(f"正在前往目的地{next_city}")
            skip = False
            while True:
                if isFight.is_fighting():
                    skip = True
                    break
                # 不再移动 说明已经到了目的地
                if not isMoved.is_moving():
                    break
            # 遇到战斗后 需要重新走一遍逻辑
            if skip:
                continue

            inputautogui.hotkey('alt', 'h')
            inputautogui.press('f9')
            if info["action"]["type"] == 0:
                x, y = info["action"]["xy"]
                # 增加随机，避免一直点一个点
                # x, y = get_random_xy(x, y)
                game_mouse.move_click(x, y)
            else:
                action = info["action"]
                click_result_1, (x_n, y_n,) = click_transport_npc(now_city, next_city)
                if not click_result_1:
                    continue
                if "button" in action:
                    click_result_2 = click_button_v2(action["button"])
                else:
                    click_result_2 = click_button('yes_i_will_go')
                if not click_result_2:
                    if click_result_1:
                        game_mouse.move_click(x_n - 100, y_n)
                        time.sleep(3)
                        inputautogui.hotkey('alt', 'h')
                        inputautogui.press('f9')
                        time.sleep(1)
                        click_result, (x_n, y_n) = click_transport_npc(now_city, next_city)
                        if not click_result:
                            logger.info("没有找到传送NPC")
                            continue
                        if "button" in action:
                            click_result_2 = click_button_v2(action["button"])
                        else:
                            click_result_2 = click_button('yes_i_will_go')
                        if not click_result_2:
                            logger.info("没有找到传送按钮")
                            continue
                        time.sleep(2)
                        continue
            time.sleep(3)
        pass


MapTask = Map(WINDOW_ID)

if __name__ == '__main__':
    # time.sleep(2)
    MapTask.MoveToTarget("凌霄宝殿", "None")
