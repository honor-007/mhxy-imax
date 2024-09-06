import os.path
import time

import win32gui

from assets.sources import get_source, basedir, props_data
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.components.InputAutoGui import inputautogui
from src.components.window import WINDOW_ID
from src.utils.globalVariable import log_queue, module_task_stop_event


class Props:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    # def __if_windows_in_screen(self) -> bool:
    #     return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd)

    def __if_windows_in_screen(self):
        """
        判断当前窗口是否是mhxy的窗口
        :return:
        """
        if module_task_stop_event.is_set():
            module_task_stop_event.clear()
            return
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == win32gui.GetWindowText(self.hwnd):
            return
        else:
            log_queue("梦幻西游不在当前窗口,请将梦幻西游窗口打开为当前窗口...")
            time.sleep(1)
            self.__if_windows_in_screen()
            return

    def openProps(self, rate=0.95):
        """
        打开道具背包
        """
        result = match_img(self.__screenshot(), get_source('props_flag'), 10, 10, rate)
        if result[3] is None:
            log_queue.put("道具行囊未打开，打开道具行囊")
            inputautogui.hotkey('alt', 'e')
            time.sleep(0.5)
            return
        else:
            log_queue.put("道具行囊已经打开,confidence:{}".format(result[3]['confidence']))
            return

    def closeProps(self, rate=0.95):
        log_queue.put("关闭行囊")
        result = match_img(self.__screenshot(), get_source('props_flag'), 10, 10, rate)
        if result[3] is None:
            log_queue.put("当前页面未检测到行囊,无法关闭")
            return
        else:
            inputautogui.hotkey('alt', 'e')
            time.sleep(0.5)
            return

    def findProps(self, name, rate=0.95):
        template = os.path.join(basedir, 'props', props_data[name])
        result = match_img(self.__screenshot(), template, 10, 10, rate)
        if result[3] is None:
            return
        return result[3]['result']

    def closeButtonToNpc(self):
        return self.findProps("确定给予")

    def isPropsToPlayer(self, rate=0.95):
        result = match_img(self.__screenshot(), get_source('props_to_player'), 10, 10, rate)
        if result[3] is None:
            return
        return result[3][result]

    def isPropsToNpc(self, rate=0.95):
        result = match_img(self.__screenshot(), get_source('props_to_npc'), 10, 10, rate)
        if result[3] is None:
            return
        return result[3]['result']


PropsFunction = Props(WINDOW_ID)
