import cv2
import pywintypes
import win32api
import win32con
import win32gui
import win32ui
import numpy as np

from src.components.window import SCREEN_SCALE
from src.utils.globalVariable import log_queue


def grab_screen(region=None):
    """
    :param region: 截图区域
    :return: 图片
    """
    hwin = win32gui.GetDesktopWindow()

    if region:
        left, top, x2, y2 = region
        left = round(left * SCREEN_SCALE)
        top = round(top * SCREEN_SCALE)
        x2 = round(x2 * SCREEN_SCALE)
        y2 = round(y2 * SCREEN_SCALE)
        width = x2 - left + 1
        height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    oldbmp = memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    memdc.SelectObject(oldbmp)
    win32gui.DeleteObject(bmp.GetHandle())
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def winShot(hwnd):
    """
    根据窗口句柄截取窗口视图
    :param hwnd: 窗口句柄 一个整数
    """
    # region = win32gui.GetWindowRect(hwnd)
    # return grab_screen(region=region)
    try:
        region = win32gui.GetWindowRect(hwnd)
    except Exception as e:
        log_queue.put(f"截取mhxy游戏窗口失败,请确认游戏窗口位于最前端")
        print(f"截取mhxy游戏窗口失败: {e}")
    else:
        return grab_screen(region=region)