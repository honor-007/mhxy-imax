import math
import random
import time
from abc import abstractmethod

import kmNet
import pyautogui

from assets.sources import system_setting
from script_utils.loggerConfig import logger


def randomOne():
    return (random.randint(0, 20)) / 10


def randomTwo():
    return random.randint(-10, 10) / 10


vk_code_kmbox = {
    "a": 4,
    "b": 5,
    "c": 6,
    "d": 7,
    "e": 8,
    "f": 9,
    "g": 10,
    "h": 11,
    "i": 12,
    "j": 13,
    "k": 14,
    "l": 15,
    "m": 16,
    "n": 17,
    "o": 18,
    "p": 19,
    "q": 20,
    "r": 21,
    "s": 22,
    "t": 23,
    "u": 24,
    "v": 25,
    "w": 26,
    "x": 27,
    "y": 28,
    "z": 29,

    "1": 30,
    "2": 31,
    "3": 32,
    "4": 33,
    "5": 34,
    "6": 35,
    "7": 36,
    "8": 37,
    "9": 38,
    "0": 39,

    "f1": 58,
    "f2": 59,
    "f3": 60,
    "f4": 61,
    "f5": 62,
    "f6": 63,
    "f7": 64,
    "f8": 65,
    "f9": 66,
    "f10": 67,
    "f11": 68,
    "f12": 69,

    "ctrl_l": 224,
    "alt_l": 226,
    "alt": 226,
    "tab": 43
}


class MouseEventInterface():
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def move_rel(self, x, y, duration):
        """
        鼠标移动
        :param x: x轴的移动距离
        :param y: y轴的移动距离
        :duration 移动所需时间
        :return:
        """
        pass

    @abstractmethod
    def move_to(self, x, y, duration):
        """
        将窗口坐标转换为屏幕坐标并移动到x,y位置
        :param x:
        :param y:
        :return:
        """
        pass

    @abstractmethod
    def right_click(self):
        """
        对鼠标加锁
        将窗口坐标转换为屏幕坐标并移动到x,y位置
        :param x:
        :param y:
        :return:
        """
        pass

    @abstractmethod
    def left_click(self):
        """
        通过opencv的模板比较获取游戏鼠标图标的坐标
        :return:
        """
        pass

    @abstractmethod
    def left_press(self):
        pass

    @abstractmethod
    def left_release(self):
        pass

    @abstractmethod
    def right_press(self):
        pass

    @abstractmethod
    def right_release(self):
        pass

    @abstractmethod
    def press(self, keys):
        """
        默认你敲击键盘
        :param key: 按键
        :return:
        """
        pass

    @abstractmethod
    def hotkey(self, *args):
        """
        组合键
        :param x:
        :param y:
        :return:
        """
        pass


speed_pyautogui = 5000
length_base = 1500


class MousePyautogui(MouseEventInterface):

    def move_rel(self, x, y, duration=0.0):
        """
        鼠标移动
        :param x: x轴的移动距离
        :param y: y轴的移动距离
        :duration 移动所需时间 s
        :return:
        """
        pyautogui.moveRel(int(x), int(y), duration=int(duration))

    def move_to(self, target_x, target_y, duration=0.0):
        pyautogui.moveTo(target_x, target_y, duration)

    def right_click(self):
        return pyautogui.rightClick()

    def left_click(self):
        return pyautogui.leftClick()

    def left_press(self):
        pyautogui.mouseDown(button='left')

    def left_release(self):
        pyautogui.mouseUp(button='left')

    def right_press(self):
        pyautogui.mouseDown(button='right')

    def right_release(self):
        pyautogui.mouseUp(button='right')

    def press(self, key):
        pyautogui.press(key)

    def hotkey(self, *args):
        pyautogui.hotkey(*args, interval=random.randint(80, 400))


class MouseKmboxEnc(MouseEventInterface):
    def __init__(self):
        print("init===")

    # 贝塞尔算法 计算下个点在x,y轴要移动的距离
    def bezierCurve(self, control_points, t):
        start_point = control_points[0]
        n = len(control_points) - 1
        result = (0, 0)
        for i in range(n + 1):
            binomial_coeff = 1
            for j in range(i):
                binomial_coeff *= (n - j) / (j + 1)
            factor = binomial_coeff * pow(t, i) * pow(1 - t, n - i)
            result = (
                result[0] + int(factor * control_points[i][0]),
                result[1] + int(factor * control_points[i][1])
            )
        return result

    def bezierMouseMove(self, startPos, targetPos, duration=5):
        onMoving = False
        controlPoints = []
        currentStep = 0
        lastTime = int(time.time_ns() / 1000000)
        defaultInterval = 7
        length = math.sqrt((targetPos[0] - startPos[0]) ** 2 + (targetPos[1] - startPos[1]) ** 2)
        # 控制点基本量 和移动长度有关系 长度1000的时候为100
        controlRange = int(100 * length / 1000)
        # 步数 和移动长度有关系 长度1000的时候为100
        steps = int(100 * length / 1000)
        if steps < 10:
            steps = 10
        if controlRange < 10:
            controlRange = 10

        while True:
            # 移动时间间隔
            Interval = defaultInterval + randomTwo() * 2

            # 移动到指定位置后则不做移动
            start_x, start_y = pyautogui.position()
            distanceToTarget = math.sqrt((start_x - targetPos[0]) ** 2 + (start_y - targetPos[1]) ** 2)

            if distanceToTarget < 5.0:
                onMoving = False
                break

            if not onMoving:
                onMoving = True

                if startPos[0] - targetPos[0] > 0:
                    control_1_x = startPos[0] - randomOne() * controlRange
                else:
                    control_1_x = startPos[0] + randomOne() * controlRange

                if startPos[1] - targetPos[1] > 0:
                    control_1_y = startPos[1] - randomOne() * controlRange
                else:
                    control_1_y = startPos[1] + randomOne() * controlRange

                control_2_x = targetPos[0] + randomTwo() * controlRange
                control_2_y = targetPos[1] + randomTwo() * controlRange
                controlPoints = [startPos, (control_1_x, control_1_y), (control_2_x, control_2_y), targetPos]

                currentStep = 0
                lastTime = int(time.time_ns() / 1000000)
            else:
                now = int(time.time_ns() / 1000000)
                if (now - lastTime) >= Interval:
                    # 利用总步数和当前步数计算t进度
                    t = currentStep / steps
                    # 计算下个移动坐标进行间隔计算，用于鼠标相对移动
                    nextPos = self.bezierCurve(controlPoints, t)

                    # 移动鼠标
                    start_x, start_y = pyautogui.position()
                    x = nextPos[0] - start_x
                    y = nextPos[1] - start_y
                    # logger.info(f"bezier算法中kmbox移动,向x轴移动{x}px,向y轴移动{y}px")
                    kmNet.enc_move_auto(x, y, duration)

                    currentStep = currentStep + 1
                    lastTime = int(time.time_ns() / 1000000)
                if currentStep > steps:
                    controlPoints = [controlPoints[3],
                                     (controlPoints[3][0] + randomTwo() * controlRange,
                                      controlPoints[3][1] + randomOne() * controlRange * 2),
                                     (targetPos[0] + randomTwo() * controlRange,
                                      targetPos[1] + randomOne() * controlRange * 2),
                                     targetPos]
                    currentStep = 0

    def move_to(self, target_x, target_y, duration=5):
        start_x, start_y = pyautogui.position()
        self.bezierMouseMove((start_x, start_y), (target_x, target_y))

    def move_rel(self, x, y, duration=5):
        """
        鼠标移动
        :param x: x轴的移动距离
        :param y: y轴的移动距离
        :duration 移动所需时间 ms
        :return:
        """
        start_x, start_y = pyautogui.position()
        logger.info(f"bezier移动,起始位置({start_x},{start_y}),向x轴移动{x}px,向y轴移动{y}px")
        self.bezierMouseMove((start_x, start_y), (start_x + x, start_y + y))

    # def move_to(self, target_x, target_y, duration=5):
    #     start_x, start_y = pyautogui.position()
    #     kmNet.enc_move_auto(target_x - start_x, target_y - start_y, duration)

    def right_click(self):
        kmNet.enc_right(1)  # 鼠标右键按下
        time.sleep(random.randint(80, 400) / 1000)
        kmNet.enc_right(0)  # 鼠标右键松开

    def left_click(self):
        kmNet.enc_left(1)
        time.sleep(random.randint(80, 400) / 1000)
        kmNet.enc_left(0)

    def left_press(self):
        kmNet.enc_left(1)

    def left_release(self):
        kmNet.enc_left(0)

    def right_press(self):
        kmNet.enc_right(1)

    def right_release(self):
        kmNet.enc_right(0)

    def press(self, key):

        key = key.lower()
        key_code = vk_code_kmbox[key]
        if not key_code:
            return
        kmNet.enc_keypress(key_code, random.randint(80, 350))

    def hotkey(self, *args):
        for key in args:
            key = key.lower()
            key_code = vk_code_kmbox[key]
            kmNet.enc_keydown(key_code)
            time.sleep(random.randint(60, 300) / 1000)
        for key in reversed(args):
            key = key.lower()
            key_code = vk_code_kmbox[key]
            kmNet.enc_keyup(key_code)
            time.sleep(random.randint(10, 100) / 1000)


if system_setting['interactor'] == '模拟键鼠':
    inputautogui = MousePyautogui()
if system_setting['interactor'] == '驱动键鼠':
    result = kmNet.init(system_setting['IP'], system_setting['Port'], system_setting['UUID'])
    if result == 0:
        logger.info("kmbox init success")
    else:
        logger.error("kmbox init fail")
    inputautogui = MouseKmboxEnc()
