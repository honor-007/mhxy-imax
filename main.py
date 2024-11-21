import sys
from tkinter.messagebox import showinfo

import ttkbootstrap as tk

import src.utils.globalVariable as gv
from assets.sources import system_setting
from src.components.window import WINDOW_ID
from src.utils import http_utils
from src.windows.applicationWindow import AppilcationGui

if __name__ == "__main__":
    # TODO 正式环境删除
    WINDOW_ID = 0
    if WINDOW_ID == -1:
        showinfo('启动失败', '未检测到游戏窗口,请先登录游戏')
    else:
        # 检查当前角色id是否可用
        http_response = http_utils.check(system_setting['character_id'])
        if http_response['checkResult']:
            gv.activate_flag = True
        # 打开脚本窗口
        root = tk.Window(themename='flatly')
        applicationGui = AppilcationGui(root)
        applicationGui.start_application_window()
