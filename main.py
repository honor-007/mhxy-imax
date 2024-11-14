import ttkbootstrap as tk
from tkinter.messagebox import *
from src.components.window import WINDOW_ID
from src.windows.activateWindow import ActivateGui
from src.windows.applicationWindow import AppilcationGui

if __name__ == "__main__":

    # character_id = activate_setting['character_id']
    # activate_code = activate_setting['activate_code']
    # # TODO 根据激活码和id发送http请求判断是否可用
    #
    if_activated = True
    root = tk.Window(themename='flatly')

    if if_activated:
        # 检查相关角色是否已经进入游戏
        if WINDOW_ID == 1:
            showerror(title='错误', message='请先确认绑定的角色进入游戏后再打开此软件')
        else:
            applicationGui = AppilcationGui(root)
            applicationGui.start_application_window()
    else:
        activateGui = ActivateGui(root)
        activateGui.start_activate_window()
