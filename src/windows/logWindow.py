
from ttkbootstrap import *
import ttkbootstrap as tk


class LogGui():

    def __init__(self, root_window):
        self.log = None
        self.window = root_window

    def init_window(self):
        font = ("TkDefaultFont", 8)
        self.log = tk.ScrolledText(self.window,wrap=tk.WORD, font=font, height=28)
        # self.log.pack(pady=20)
        self.log.pack(fill=tk.BOTH, expand=True)

    def add_end_log(self, text):
        """
        向Text widget中添加文本，模拟控制台输出
        """
        self.log.insert(tk.END, text + '\n')  # 在Text widget的末尾插入文本，并添加换行符
        # 自动滚动到Text widget的末尾
        self.log.yview(tk.END)

