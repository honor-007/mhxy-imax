import random
import time
from time import sleep

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
    return random.randint(x_min, x_max), random.randint(y_min, y_max)


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
    return False


def if_mouse_using():
    try:
        with open(get_source("mouse_status"), 'r') as f:
            return f.read().strip() == '1'
    except PermissionError:
        return True


def set_mouse_not_using():
    with open(get_source("mouse_status"), 'w') as f:
        f.write('0')


def locked_mouse(function):
    """
    装饰器，在操作鼠标时对鼠标进行占用，防止多线程/多进程时鼠标有多个控制源
    :param function:
    :return:
    """

    def inner(*args, **kwargs):
        with open(get_source("mouse_status"), 'w') as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            f.write('1')
            f.flush()
            try:
                return function(*args, **kwargs)
            finally:
                f.seek(0)
                f.write('0')
                f.truncate()

    return inner


class Mouse:
    """
    游戏内指针的相关操作
    """

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)

    def __get_client_size(self):
        """获取窗口客户区宽高"""
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        return right - left, bottom - top

    def __get_safe_edge_rect(self):
        """获取10%~90%的边缘安全区域"""
        w, h = self.__get_client_size()
        return int(w * 0.2), int(h * 0.3), int(w * 0.8), int(h * 0.7)

    def __random_safe_point(self):
        """在窗口20%~80%的安全区域内生成随机坐标（窗口相对坐标）"""
        w, h = self.__get_client_size()
        client_x, client_y = random.randint(int(w * 0.3), int(w * 0.7)), random.randint(int(h * 0.3), int(h * 0.7))
        return client_x, client_y

    def __screenshot(self):
        return winShot(self.hwnd)

    def __save_debug_image(self, image, prefix="debug", extra_info=""):
        """
        保存调试图像到本地
        :param image: 要保存的图像(numpy数组)
        :param prefix: 文件名前缀
        :param extra_info: 额外信息，会添加到文件名中
        :return: 保存的文件路径
        """
        import os
        from datetime import datetime
        # 保存图像到项目根目录的debug_mouse文件夹
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        debug_dir = os.path.join(project_root, "debug_mouse")
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        if extra_info:
            filename = os.path.join(debug_dir, f"{prefix}_{extra_info}_{timestamp}.png")
        else:
            filename = os.path.join(debug_dir, f"{prefix}_{timestamp}.png")
        cv2.imwrite(filename, image)
        logger.info(f"调试图像已保存: {filename}")
        return filename

    def __client_move(self, x, y):
        """
        根据相对坐标移动到窗口的指定位置
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
        time.sleep(5)
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

    def get_mouse_point(self, retry=5, method=cv2.TM_CCORR_NORMED, show_debug=False):
        """
        获取计算出来的坐标，(包含截图顶部)
        :param retry:尝试最大次数
        :param method: 匹配方法
        :param show_debug: 是否显示调试图像（带红框标注）
        :return: 矩形左上角坐标，即鼠标点点的坐标
        """
        screenshot = self.__screenshot()
        result = match_img(screenshot, get_source("mouse_template"), 10, 10, 0.995, mask=None, method=method)
        s_x, s_y = 500, 300
        while result[3] is None and retry >= 0:
            if mouse_stop_event.is_set():
                return 0
            logger.info(f"未检测到鼠标,剩余尝试次数{retry}")
            s_x, s_y = self.__random_safe_point()
            logger.info(f"因未检测到鼠标,需要将鼠标随机移动位置后重新检测,现将鼠标随机移动到({s_x},{s_y})")
            self.__client_move(s_x, s_y)
            screenshot = self.__screenshot()
            result = match_img(screenshot, get_source("mouse_template"), 10, 10, 0.995, mask=None,
                               method=method)
            retry = retry - 1

            # 如果开启调试模式，绘制红框并保存图像
            if show_debug:
                # 使用抽象方法保存图像
                self.__save_debug_image(screenshot)

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

    def __go_game_rectangle(self, x, y, bias=3, max_approach_count=20, short_move_rate=5.0, long_move_rate=2.0):
        """
        将游戏内鼠标移动到指定的窗口坐标位置。
        采用"先大距离粗移、再小距离逼近"的两阶段策略，模拟人类鼠标移动轨迹。

        移动流程:
        1. 判断目标坐标是否靠近窗口边缘:
           - 靠近边缘: 使用相对位移(move_rel)按 long_move_rate 缩放后粗略移动，避免鼠标移出窗口
           - 不靠近边缘: 直接使用绝对坐标(client_move)一步到位
        2. 粗移后检查鼠标是否仍在窗口内，若移出则增大 long_move_rate 重试
        3. 进入循环逼近阶段，通过 kmNet 硬件级小幅移动不断修正偏差，直到游戏鼠标
           到达目标坐标(误差在 bias 范围内)或达到最大尝试次数

        :param x: mhxy窗口目标x坐标
        :param y: mhxy窗口目标y坐标
        :param bias: 允许的坐标误差范围(像素)
        :param max_approach_count: 逼近阶段允许的最大循环次数
        :param short_move_rate: 逼近阶段的移动缩放系数，值越大每次移动越小，精度越高
        :param long_move_rate: 粗移阶段的移动缩放系数，值越大首次移动距离越短
        :return: 0 表示成功到达或被中断，1 表示超出最大尝试次数
        """
        x = int(x)
        y = int(y)
        logger.info(f"游戏鼠标目标坐标x:{x},y:{y},允许误差:{bias},开始移动...")

        # ========== 第一阶段: 大距离粗移（循环重试代替递归） ==========
        edge_x_min, edge_y_min, edge_x_max, edge_y_max = self.__get_safe_edge_rect()
        is_near_edge = (x < edge_x_min or x > edge_x_max
                        or y < edge_y_min or y > edge_y_max)

        coarse_moved = False
        max_coarse_retry = 10
        for _ in range(max_coarse_retry):
            if mouse_stop_event.is_set():
                return 0

            if is_near_edge:
                # 边缘目标使用更大的缩放系数，减小每次移动幅度
                short_move_rate = max(short_move_rate, 3)
                # 如果鼠标当前不在窗口内，先随机移回窗口中央区域
                if not self.__mouse_in_window():
                    rand_x, rand_y = self.__random_safe_point()
                    self.__client_move(rand_x, rand_y)
                # 获取当前游戏鼠标在窗口内的相对坐标
                mouse_x, mouse_y = self.get_mouse_point()
                if if_arrived(x, y, mouse_x, mouse_y, bias=bias):
                    return 0
                # 按 long_move_rate 缩放后进行相对位移，快速靠近目标点
                dxs = int((x - mouse_x) / long_move_rate)
                dys = int((y - mouse_y) / long_move_rate)
                logger.info(f"大距离粗移,鼠标向x:{dxs},y:{dys}方向移动")
                inputautogui.move_rel(dxs, dys)
            else:
                # 目标不靠近边缘，直接用绝对坐标一步移动到位
                logger.info(f"目标位置不靠近边缘,直接移动到x:{x},y:{y}")
                self.__client_move(x, y)

            # 粗移后检查鼠标是否还在窗口内
            if self.__mouse_in_window():
                coarse_moved = True
                break
            else:
                long_move_rate += 0.5
                logger.info(f"粗移后鼠标移出窗口,增大long_move_rate至{long_move_rate}重试")
                self.__client_move(x, y)

        if not coarse_moved:
            logger.warning("粗移阶段多次重试后鼠标仍在窗口外")
            return 1

        tempX, tempY = pyautogui.position()
        logger.info(f"粗移完成，当前鼠标位置({tempX},{tempY})")

        # 粗移完成后，获取当前游戏鼠标位置，准备进入逼近阶段
        x_moved, y_moved = self.get_mouse_point(show_debug=True)

        # ========== 第二阶段: 循环逼近目标坐标 ==========
        s_count = 1
        while not if_arrived(x, y, x_moved, y_moved, bias=bias) and s_count <= max_approach_count:
            if mouse_stop_event.is_set():
                return 0
            # 确保梦幻西游窗口仍在前台
            self.__if_windows_in_screen()
            # 如果鼠标移出了窗口，先移回窗口内，增大 short_move_rate 减小步幅后继续逼近
            if not self.__mouse_in_window():
                logger.info(
                    f"逼近时鼠标移出窗口,short_move_rate:{short_move_rate},增大至{short_move_rate + 0.2}")
                short_move_rate += 0.2
                rand_x, rand_y = self.__random_safe_point()
                self.__client_move(rand_x, rand_y)
                x_moved, y_moved = self.get_mouse_point(show_debug=True)
                continue

            # 通过 kmNet 硬件进行小幅相对移动，逐步逼近目标
            dx = int((x - x_moved) / short_move_rate)
            dy = int((y - y_moved) / short_move_rate)
            # TODO 这里有问题 逼近阶段,鼠标向x:397,y:68方向移动
            logger.info(f"逼近阶段,目标相对坐标({x},{y})")
            logger.info(f"逼近阶段,当前鼠标相对位置({x_moved},{y_moved})")
            logger.info(f"逼近阶段,鼠标向x:{dx},y:{dy}方向移动")
            # 按缩放系数缩小移动距离，避免过冲
            kmNet.enc_move_auto(dx, dy, int(2000/s_count))

            # 每次移动后重新获取游戏鼠标位置，用于下一轮判断
            x_moved, y_moved = self.get_mouse_point(show_debug=True)
            s_count += 1
            if s_count > max_approach_count:
                logger.warning("鼠标逼近目标超出最大循环次数")
                return 1
        logger.info("游戏鼠标完成移动!!!")
        return 0

    def __if_windows_in_screen(self):
        """
        判断当前窗口是否是mhxy的窗口
        :return:
        """
        while True:
            if module_task_stop_event.is_set():
                return
            if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name:
                return
            log_queue("梦幻西游不在当前窗口,请将梦幻西游窗口打开为当前窗口...")
            time.sleep(1)

    def __left_click(self):
        return inputautogui.left_click()

    def __right_click(self):
        return inputautogui.right_click()

    @locked_mouse
    def move(self, x, y, bias=3):
        """
        移动鼠标到指定坐标（xy窗口相对坐标）
        """
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
