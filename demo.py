import threading
import time
from tkinter import *

import win32gui

from src.utils.globalVariable import auto_fight_stop_event


def __if_windows_in_screen():
    """
    判断当前窗口是否是mhxy的窗口
    :return:
    """
    if auto_fight_stop_event.is_set():
        auto_fight_stop_event.clear()
        return
    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == 'menghuanxiyou':
        return
    else:
        print("屏幕不在当前桌面")
        time.sleep(1)
        __if_windows_in_screen()
        return

def stop():
    time.sleep(3)
    auto_fight_stop_event.set()

auto_fight_thread = threading.Thread(target=stop)
auto_fight_thread.start()
__if_windows_in_screen()