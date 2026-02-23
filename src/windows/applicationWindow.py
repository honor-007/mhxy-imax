import threading

import ttkbootstrap as tk
from ttkbootstrap.dialogs.dialogs import Messagebox

from assets.sources import system_setting
from src.components.gui_components import FONT_SMALL
from script_utils.loggerConfig import logger
from src.utils.globalVariable import *
from src.windows import escortWindow, autoFightWindow, systemWindow, logWindow, activeWindow
from src.utils import globalVariable


class AppilcationGui():
    """程序主窗口"""

    def __init__(self, root_window):
        self.log_gui = None
        self.page_log = None
        self.notebook = None
        self.previous_tab = 0
        self.root = root_window
        self.task = None
        globalVariable.character_id = tk.StringVar(value=system_setting['character_id'])

    def init_window(self):
        self.root.title("MHXY 辅助工具 v1.0")
        self.root.geometry('1100x480+10+10')
        self.root.iconbitmap(r'./icon.ico')

        # 创建导航栏
        self.task = tk.Frame(self.root)
        self.task.grid(row=0, column=0, padx=5, pady=(5, 0), sticky='nsew')

        # 创建 Notebook
        self.notebook = tk.Notebook(self.task, bootstyle="primary")
        self.notebook.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # 初始化页面
        page_escort = tk.Frame(self.notebook)
        page_zhuogui = tk.Frame(self.notebook)
        page_datu = tk.Frame(self.notebook)
        page_paoshang = tk.Frame(self.notebook)
        page_afk = tk.Frame(self.notebook)
        page_system = tk.Frame(self.notebook)
        page_active = tk.Frame(self.notebook)

        self.notebook.add(page_escort, text='  押镖  ')
        self.notebook.add(page_zhuogui, text='  捉鬼  ')
        self.notebook.add(page_datu, text='  打图  ')
        self.notebook.add(page_paoshang, text='  跑商  ')
        self.notebook.add(page_afk, text='  挂机  ')
        self.notebook.add(page_system, text=' 系统设置 ')
        self.notebook.add(page_active, text='  激活  ')
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # 初始化各 tab 内容
        escort_gui = escortWindow.EscortGui(page_escort)
        escort_gui.init_window()

        tk.Label(page_zhuogui, text="敬请期待", font=FONT_SMALL).pack(pady=30)
        tk.Label(page_datu, text="敬请期待", font=FONT_SMALL).pack(pady=30)
        tk.Label(page_paoshang, text="敬请期待", font=FONT_SMALL).pack(pady=30)

        auto_fight_gui = autoFightWindow.AutoFightGui(page_afk)
        auto_fight_gui.init_window()

        active_gui = activeWindow.ActiveGui(page_active)
        active_gui.init_window()

        system_gui = systemWindow.SystemGui(page_system)
        system_gui.init_window()

        # 日志面板
        self.page_log = tk.Frame(self.root)
        self.page_log.grid(row=0, column=1, padx=(5, 10), pady=5, sticky='nsew')
        self.log_gui = logWindow.LogGui(self.page_log)
        self.log_gui.init_window()

        # 让日志面板可以自适应
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        module_task_stop_event.set()

    def on_tab_change(self, event):
        target_tab = event.widget.index(event.widget.select())
        if not module_task_stop_event.is_set() and target_tab != self.previous_tab:
            self.notebook.select(self.previous_tab)
            Messagebox.show_warning("切换模块前请先关闭任务！", "警告")
        else:
            self.previous_tab = target_tab
        globalVariable.character_id.set(system_setting['character_id'])
        logger.info(f"Tab changed to index: {target_tab}")

    def log_info(self):
        while not log_stop_event.is_set():
            item = log_queue.get()
            if log_stop_event.is_set():
                break
            logger.info(item)
            self.log_gui.add_end_log(item)
            log_queue.task_done()
        logger.info("日志task退出")

    def on_close_application_window(self):
        stop_event_all_set()
        log_queue.put("窗口关闭...")
        logger.info("application窗口关闭...")
        self.root.destroy()

    def start_application_window(self):
        self.init_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_application_window)
        t = threading.Thread(target=self.log_info, args=())
        t.start()
        logger.info("任务未启动...")
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Window(themename='flatly')
    applicationGui = AppilcationGui(root)
    applicationGui.start_application_window()
