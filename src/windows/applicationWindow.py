from ttkbootstrap import *
import ttkbootstrap as tk
from ttkbootstrap.dialogs.dialogs import Messagebox

from script_utils.loggerConfig import logger
from src.utils.globalVariable import *
from src.windows import escortWindow, autoFightWindow, systemWindow, logWindow


class AppilcationGui():
    """
    程序主窗口
    """

    def __init__(self, root_window):
        # super().__init__()
        self.log_gui = None
        self.page_log = None
        self.notebook = None
        self.previous_tab = 0  # 用于记录之前的tab
        self.root = root_window
        self.task = None

    def init_window(self):
        self.root.title("MHXY 辅助工具 v1.0")  # 窗口名
        self.root.geometry('1050x450+10+10')  # 290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.root.iconbitmap(r'./icon.ico')

        # 创建导航栏
        self.task = tk.Frame(self.root, height=30)
        self.task.grid(row=0, column=0, padx=2, pady=(2, 0), ipadx=0, ipady=0, sticky=tk.W)

        # 创建页面按钮
        self.notebook = tk.Notebook(self.task, bootstyle="primary")
        self.notebook.grid(row=0, column=0, padx=10, pady=2, ipadx=0, ipady=0, sticky='n')

        # 初始化页面Frame
        page_escort = tk.Frame(self.notebook)
        page_zhuogui = tk.Frame(self.notebook)
        page_datu = tk.Frame(self.notebook)
        page_afk = tk.Frame(self.notebook)
        page_system = tk.Frame(self.notebook)

        # 添加标签页到 Notebook
        self.notebook.add(page_escort, text='  押镖  ')
        self.notebook.add(page_zhuogui, text='  捉鬼  ')
        self.notebook.add(page_datu, text='  打图  ')
        self.notebook.add(page_datu, text='  跑商  ')
        self.notebook.add(page_afk, text='  挂机  ')
        self.notebook.add(page_system, text=' 系统设置 ')
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        # tab页内容
        escort_gui = escortWindow.EscortGui(page_escort)
        escort_gui.init_window()
        tk.Label(page_zhuogui, text="zhuogui").pack(pady=20)
        tk.Label(page_datu, text="datu").pack(pady=20)
        tk.Label(page_datu, text="paoshang").pack(pady=20)
        auto_fight_gui = autoFightWindow.AutoFightGui(page_afk)
        auto_fight_gui.init_window()

        system_gui = systemWindow.SystemGui(page_system)
        system_gui.init_window()

        # Separator(self, orient=VERTICAL).grid(row=2, column=1, columnspan=1, sticky='ns', pady=(5, 5))
        self.page_log = tk.Frame(self.root)
        self.page_log.grid(row=0, column=1, padx=10, pady=2, ipadx=0, ipady=10, sticky='s')  # sticky='n' 粘附上边缘 north
        self.log_gui = logWindow.LogGui(self.page_log)
        self.log_gui.init_window()
        # font = ("TkDefaultFont", 10)
        # self.log = ScrolledText(self.page_log, wrap=tk.WORD, font=font, height=25)
        # self.log.pack(fill=tk.BOTH, expand=True)
        module_task_stop_event.set()

    def on_tab_change(self, event):
        # 获取当前选中的tab的索引
        target_tab = event.widget.index(event.widget.select())
        if not module_task_stop_event.is_set() and target_tab != self.previous_tab:
            self.notebook.select(self.previous_tab)
            Messagebox.show_warning("警告", "切换模块前请先关闭任务！")
        else:
            self.previous_tab = target_tab

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
        print("start_application_window===========")
        self.init_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_application_window)
        # 启动线程
        t = threading.Thread(target=self.log_info, args=())
        t.start()
        logger.info("任务未启动...")
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Window(themename='flatly')
    applicationGui = AppilcationGui(root)
    applicationGui.start_application_window()
