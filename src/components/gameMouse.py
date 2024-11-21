import random
import random
import time

import cv2
import kmNet
import portalocker
import pyautogui
# import pyautogui
import win32gui

from assets.sources import get_source
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.components.InputAutoGui import inputautogui
from src.components.window import WINDOW_ID
from src.utils.globalVariable import mouse_stop_event, module_task_stop_event, log_queue


def start_point(x_min, y_min, x_max, y_max):
    """
    随机生成一个起始点
    :param x_min:
    :param y_min:
    :param x_max:
    :param y_max:
    :return: 坐标
    """
    return random.randint(x_min, x_max), random.uniform(y_min, y_max)


def if_arrived(x1, y1, x2, y2, bias=3):
    """
    判断坐标1和坐标二是否一致
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :param bias:
    :return:
    """
    x_abs = abs(x1 - x2)
    y_abs = abs(y1 - y2)
    if x_abs <= bias and y_abs <= bias:
        logger.info(f"最终鼠标到达目的位置准确坐标:x:{x2},y:{y2}")
        return True
    # return x_abs <= bias and y_abs <= bias


def if_mouse_using():
    f = open(get_source("mouse_status"), 'r')
    try:
        status = f.read().strip()
    except PermissionError:
        return True
    f.close()
    if status == '1':
        return True
    else:
        return False


def set_mouse_not_using():
    f = open(get_source("mouse_status"), 'w')
    f.write('0')
    f.close()


def locked_mouse(function):
    """
    装饰器，在操作鼠标时对鼠标进行占用，防止多线程/多进程时鼠标有多个控制源
    :param function:
    :return:
    """

    def inner(*args, **kwargs):
        while True:
            if not if_mouse_using():
                break
        # 告诉鼠标被控制
        f = open(get_source("mouse_status"), 'w')
        portalocker.lock(f, portalocker.LOCK_EX)  # 加锁
        f.write('1')
        function(*args, **kwargs)
        f.write('0')
        f.close()

    return inner


class Mouse:
    """
    游戏内指针的相关操作
    """
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)

    # def rel_move(self, x, y, speed=5000):
    #     """
    #     鼠标移动
    #     :param x: x轴的移动距离
    #     :param y: y轴的移动距离
    #     :duration 移动所需时间
    #     :return:
    #     """
    #     length = math.sqrt(x ** 2 + y ** 2)
    #     speed = random.randint(8, 12) / 10 * speed
    #     duration = length / speed
    #     # TODO
    #     pyautogui.moveRel(int(x), int(y), duration=int(duration))

    def __screenshot(self):
        return winShot(self.hwnd)

    def __client_move(self, x, y):
        """
        将窗口坐标转换为屏幕坐标并移动到x,y位置
        :param x:
        :param y:
        :return:
        """
        # if not self.__if_windows_in_screen():
        #     log_queue("梦幻西游不在当前窗口,无法进行游戏鼠标移动...")
        #     return
        self.__if_windows_in_screen()
        # 将窗口坐标转换为屏幕坐标
        x, y = win32gui.ClientToScreen(self.hwnd, (int(x), int(y)))
        logger.info(f"开始移动鼠标到屏幕({x},{y})")
        inputautogui.move_to(x, y)
        time.sleep(0.15)
        return x, y

    @locked_mouse
    def locked_client_move(self, x, y):
        # if not self.__if_windows_in_screen():
        #     log_queue("梦幻西游不在当前窗口,无法进行游戏鼠标移动...")
        #     return
        self.__if_windows_in_screen()
        x, y = win32gui.ClientToScreen(self.hwnd, (int(x), int(y)))
        logger.info(f"开始移动鼠标到屏幕({x},{y})")
        inputautogui.move_to(x, y)
        time.sleep(0.15)
        return x, y

    def get_mouse_point(self, retry=5, method=cv2.TM_CCORR_NORMED):
        """
        获取计算出来的坐标，(包含截图顶部)
        :param retry:尝试最大次数
        :return: 矩形左上角坐标，即鼠标点点的坐标
        """
        result = match_img(self.__screenshot(), get_source("mouse_template"), 10, 10, 0.98, mask=None, method=method)
        s_x, s_y = 500, 300
        while result[3] is None and retry >= 0:
            if mouse_stop_event.is_set():
                return 0
            logger.info(f"未检测到鼠标,剩余尝试次数{retry}")
            s_x, s_y = start_point(200, 900, 200, 600)
            logger.info(f"因未检测到鼠标,需要将鼠标随机移动位置后重新检测,现将鼠标随机移动到({s_x},{s_y})")
            self.__client_move(s_x, s_y)
            result = match_img(self.__screenshot(), get_source("mouse_template"), 10, 10, 0.98, mask=None,
                               method=method)
            retry = retry - 1
        if result[3] is None:
            logger.warning("未能识别出游戏鼠标")
            return s_x, s_y
        else:
            x, y = result[3]['rectangle'][0]
            # logger.info(f"识别出游戏鼠标,坐标位置({x - 8},{y - 8})")
            return x - 8, y - 8

    def __mouse_in_window(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        x, y = pyautogui.position()
        if left <= x < right and top <= y < bottom:
            return True
        else:
            logger.warning(
                f"鼠标位置不在游戏窗口内,鼠标坐标:({x},{y}),窗口坐标:left:{left}, top:{top}, right:{right}, bottom:{bottom}")
            return False

    def __go_game_rectangle(self, x, y, bias=0, count=20, short_move_rate=2.0, long_move_rate=2.0):
        """

        :param x: mhxy窗口目标x坐标
        :param y: mhxy窗口目标y坐标
        :param bias: 允许误差范围
        :param count: 允许最大递归次数
        :return:
        """
        x = int(x)
        y = int(y)
        logger.info(f"游戏鼠标目标坐标x:{x},y:{y},允许误差:{bias},开始移动...")
        # short_move_rate = 1.5
        # long_move_rate = 1.6
        # 相对坐标未超出范围(坐标点太靠近边框的要特殊处理,防止因为偏移到窗口外面去)
        if x < 100 or x > 900 or y < 50 or y > 650:
            short_move_rate = 3
            # 判断鼠标是否在梦幻西游窗口内
            if not self.__mouse_in_window():
                # 移动到mhxy窗口内的一个随机坐标
                self.__client_move(start_point(200, 900, 200, 600)[0], start_point(200, 900, 200, 600)[1])
            # 获取当前mhxy窗口内鼠标的相对窗口的位置
            mouse_x, mouse_y = self.get_mouse_point()
            if not if_arrived(x, y, mouse_x, mouse_y, bias=bias):
                # 第一次大距离移动 靠近目标点 采用(加速 快速 贝塞尔曲线移动)
                dxs = int((x - mouse_x) / long_move_rate)
                dys = int((y - mouse_y) / long_move_rate)
                logger.info(f"第一次大距离移动,鼠标向x:{dxs},y:{dys}坐标移动 ")
                inputautogui.move_rel(dxs, dys)
            else:
                return 0
        else:
            logger.info(f"目标位置不靠近边缘,没有移出窗口的风险,移动距离不做处理")
            logger.info(f"第一次大距离移动,鼠标向x{x},y{y}坐标移动")
            self.__client_move(x, y)

        if not self.__mouse_in_window():
            logger.info(
                f"第一次大距离移动时,鼠标移动出了窗口,当前long_move_rate:{long_move_rate},改为{long_move_rate + 0.5}进行尝试")
            if mouse_stop_event.is_set():
                return 0
            self.__client_move(x, y)
            self.__go_game_rectangle(x, y, long_move_rate=long_move_rate + 0.5)
            return 0

        x_moved, y_moved = self.get_mouse_point()

        # 逼进坐标
        s_count = 1
        while not if_arrived(x, y, x_moved, y_moved, bias=bias) and s_count <= count:
            if mouse_stop_event.is_set():
                return 0
            kmbox_x, kmbox_y = pyautogui.position()
            # logger.info(f"开始循环逼近目标点({x},{y}),当前游戏坐标({x_moved},{y_moved}),当前鼠标坐标({kmbox_x},{kmbox_y})")
            # if not self.__if_windows_in_screen():
            #     logger.info(
            #         f"鼠标循环逼近时,mhxy窗口不在当前页面,退出操作")
            #     return
            self.__if_windows_in_screen()
            # 如果鼠标不在窗口内了,需要先将鼠标移动到最后一次游戏鼠标的位置,然后再执行__go_game_rectangle()方法
            if not self.__mouse_in_window():
                # result = self.__client_move(start_point(200, 900, 200, 600)[0], start_point(200, 900, 200, 600)[1])
                logger.info(
                    f"鼠标循环逼近时,鼠标移动出了窗口,short_move_rate:{short_move_rate},改为{short_move_rate + 0.5}进行尝试")
                self.__client_move(start_point(200, 900, 200, 600)[0], start_point(200, 900, 200, 600)[1])
                self.__go_game_rectangle(x, y, bias, short_move_rate=short_move_rate + 0.2)
                return 0

            # 这里小范围移动应该采用 直线慢速移动
            if int((x - x_moved) / short_move_rate) == 0 or int((y - y_moved) / short_move_rate) == 0:
                # logger.info(f"鼠标向x轴移动{int((x - x_moved))}px,向y轴移动{int((y - y_moved))}px")
                kmNet.enc_move_auto(int((x - x_moved)), int((y - y_moved)), random.randint(20, 50))
            else:
                # logger.info(
                #     f"鼠标move_rate向x轴移动{int((x - x_moved) / move_rate)}px,向y轴移动{int((y - y_moved) / move_rate)}px")
                kmNet.enc_move_auto(int((x - x_moved) / short_move_rate), int((y - y_moved) / short_move_rate),
                                    random.randint(20, 50))
            x_moved, y_moved = self.get_mouse_point()
            s_count = s_count + 1
            if s_count > count:
                logger.warning("鼠标移动一个地方超出最大次数,可移动次数")
                return 1
        return 0

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

    def __left_click(self):
        return inputautogui.left_click()

    def __right_click(self):
        return inputautogui.right_click()

    @locked_mouse
    def move(self, x, y, bias=3):
        self.__go_game_rectangle(x, y, bias=bias)
        return self.get_mouse_point()

    @locked_mouse
    def move_click(self, x, y, bias=3):
        self.__go_game_rectangle(x, y, bias=bias)
        self.__left_click()
        return self.get_mouse_point()

    @locked_mouse
    def move_right_click(self, x, y, bias=3):
        self.__go_game_rectangle(x, y, bias=bias)
        self.__right_click()
        return self.get_mouse_point()

    @locked_mouse
    def left_click(self):
        return self.__left_click()

    @locked_mouse
    def right_click(self):
        return self.__right_click()


set_mouse_not_using()
game_mouse = Mouse(WINDOW_ID)
