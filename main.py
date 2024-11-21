import ttkbootstrap as tk

import src.utils.globalVariable as gv
from assets.sources import activate_setting
from src.utils import http_utils
from src.windows.applicationWindow import AppilcationGui

if __name__ == "__main__":
    # 检查当前角色id是否可用
    http_response = http_utils.check(activate_setting['character_id'])
    if http_response['checkResult']:
        gv.activate_flag = True
    # 打开脚本窗口
    root = tk.Window(themename='flatly')
    applicationGui = AppilcationGui(root)
    applicationGui.start_application_window()
