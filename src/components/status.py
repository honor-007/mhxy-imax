import time

import cv2
import win32gui

from assets.sources import get_source
from src.components.window import WINDOW_ID
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import crop_image_data, compare_image, match_img
from src.utils.globalVariable import module_task_stop_event, log_queue


class Fight:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def is_fighting(self):
        """
        判断是否进入战斗
        :return:
        """
        img = crop_image_data(self.__screenshot(), (1012, 120), (1020, 385))
        rate = compare_image(img, get_source('fight_template'), channel_axis=True)
        if rate > 0.98:
            return True
        return False

    def is_need_fight_action(self):
        """
        判断是否需要战斗操作
        :return:
        """
        img = crop_image_data(self.__screenshot(), (892, 236), (953, 531))
        result = match_img(img, get_source('fight_action'), 10, 10, 0.95)
        if result[2] is not None and float(result[2]) > 0.95:
            return True

        img = crop_image_data(self.__screenshot(), (892, 236), (953, 433))
        result = match_img(img, get_source('short_fight_action'), 10, 10, 0.95)
        if result[2] is not None and float(result[2]) > 0.95:
            return True

        return False


class IsMovedTask:
    def __init__(self, hwnd):
        self._running = True
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)
        self.range = [(196, 195), (147, 600), (801, 84), (884, 641)]

    def terminate(self):
        self._running = False

    # def __if_windows_in_screen(self):
    #     return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name

    def __if_windows_in_screen(self):
        """
        判断当前窗口是否是mhxy的窗口
        :return:
        """
        if module_task_stop_event.is_set():
            module_task_stop_event.clear()
            return
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name:
            return
        else:
            log_queue("梦幻西游不在当前窗口,请将梦幻西游窗口打开为当前窗口...")
            time.sleep(1)
            self.__if_windows_in_screen()
            return

    def is_moving(self, sleep_time=1):
        """
        判断当前是否在移动 靠四个特征点判断前后是否相同来判断是否正在移动
        :param sleep_time:
        :return:
        """
        self.__if_windows_in_screen()
        crop_data_pre = []
        for crop_rectangle in self.range:
            x, y = crop_rectangle
            screenshot = winShot(self.hwnd)
            re = crop_image_data(screenshot, (x - 15, y - 15), (x + 15, y + 15))
            crop_data_pre.append(re)
        time.sleep(sleep_time)
        crop_data_later = []
        for crop_rectangle in self.range:
            x, y = crop_rectangle
            screenshot = winShot(self.hwnd)
            re = crop_image_data(screenshot, (x - 15, y - 15), (x + 15, y + 15))
            crop_data_later.append(re)
        for i in range(len(self.range)):
            rate = compare_image(crop_data_pre[i], crop_data_later[i])
            if rate >= 0.97:
                logger.info("Player have stop move")
                return False
        else:
            return True


isFight = Fight(WINDOW_ID)
isMoved = IsMovedTask(WINDOW_ID)
