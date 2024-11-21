import ttkbootstrap as tk
from tkinter.messagebox import *

from assets.sources import activate_setting
from src.windows.applicationWindow import AppilcationGui
import src.utils.globalVariable as gv
from src.utils import http_utils

if __name__ == "__main__":
    character_id = activate_setting['character_id']

    http_response = http_utils.check(character_id)
    if http_response['checkResult']:
        gv.activate_flag = True

    root = tk.Window(themename='flatly')
    applicationGui = AppilcationGui(root)
    applicationGui.start_application_window()
