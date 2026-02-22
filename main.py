from tkinter.messagebox import showinfo

import ttkbootstrap as tk
from src.windows.applicationWindow import AppilcationGui

if __name__ == "__main__":
    # TODO 正式环境删除
    WINDOW_ID = 0
    if WINDOW_ID == -1:
        showinfo('启动失败', '未检测到游戏窗口,请先登录游戏')
    else:
        # 打开脚本窗口
        root = tk.Window(themename='flatly')
        applicationGui = AppilcationGui(root)
        applicationGui.start_application_window()
