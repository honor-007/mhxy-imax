
from ttkbootstrap import *
import ttkbootstrap as tk
from src.components.gui_components import FONT_SMALL


class LogGui():

    def __init__(self, root_window):
        self.log = None
        self.window = root_window

    def init_window(self):
        self.log = tk.ScrolledText(self.window, wrap=tk.WORD, font=FONT_SMALL, height=26)
        self.log.pack(fill=tk.BOTH, expand=True)

    def add_end_log(self, text):
        """向Text widget中添加文本，模拟控制台输出"""
        self.log.insert(tk.END, text + '\n')
        self.log.yview(tk.END)
