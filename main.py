import ttkbootstrap as tk

from src.windows.activateWindow import activateGui
from src.windows.applicationWindow import AppilcationGui

if __name__ == "__main__":
    # character_id = activate_setting['character_id']
    # activate_code = activate_setting['activate_code']
    # # TODO 根据激活码和id发送http请求判断是否可用
    #
    if_activated = True
    if if_activated:
        root = tk.Window(themename='flatly')
        applicationGui = AppilcationGui(root)
        applicationGui.start_application_window()
    else:
        activateGui.start_activate_window()
