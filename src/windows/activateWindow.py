import webbrowser

import ttkbootstrap as tk
from ttkbootstrap.dialogs import Messagebox

from assets.sources import activate_setting
from script_utils.loggerConfig import logger
from src.windows.applicationWindow import AppilcationGui


class ActivateGui():
    """
    激活窗口
    """

    def __init__(self,root_window):
        self.root = root_window

    def init_window(self):
        # self.root = tk.Window(themename='flatly')
        self.root.title("MHXY辅助工具 激活")  # 窗口名
        self.root.geometry('600x450+10+10')  # 290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.root.iconbitmap(r'icon.ico')

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        width = 32
        font = ("TkDefaultFont", 12)

        message_str = "欢迎使用!"
        title = tk.Label(self.root, text=message_str, wraplength=500, font=("TkDefaultFont", 12, 'bold'))
        title.grid(row=0, column=0, padx=50, pady=(40, 0), ipadx=0, ipady=0, columnspan=2)

        message_str = "    本产品需要配合kmbox硬件使用以规避游戏的键鼠检测,激活前请确认您已拥有kmbox以避免不必要浪费.kmbox购买链接:http://www.taobao.com.本产品7天试用搭配淘宝7天无理由退货,以确保您使用效果不佳不会造成任何损失."

        message = tk.Label(self.root, text=message_str, wraplength=500, font=font, bootstyle=tk.PRIMARY)
        message.grid(row=1, column=0, padx=50, pady=(20, 5), ipadx=0, ipady=0, columnspan=2)
        message_str = "声明:kmbox是第三方产品,本脚本只是借助其功能,并未与其有任何关系"
        message = tk.Label(self.root, text=message_str, wraplength=500, font=("TkDefaultFont", 10), bootstyle=tk.DANGER)
        message.grid(row=2, column=0, padx=50, pady=(5, 10), ipadx=0, ipady=0, columnspan=2)

        id_label = tk.Label(self.root, text='角色ID:')
        id_label.grid(row=5, column=0, padx=2, pady=2, ipadx=0, ipady=0, sticky='e')

        entry_id = tk.Entry(self.root, font=font, width=width + 2)
        entry_id.bind("<KeyRelease>", self.on_id_change)
        entry_id.grid(row=5, column=1, padx=2, pady=2, ipadx=0, ipady=0, sticky='w')

        activate_code_label = tk.Label(self.root, text='激活码:')
        activate_code_label.grid(row=6, column=0, padx=2, pady=2, ipadx=0, ipady=0, sticky='en')

        entry_activate_code = tk.Text(self.root, font=font, width=width + 2, height=5)
        entry_activate_code.bind("<KeyRelease>", self.on_activate_code_change)
        entry_activate_code.grid(row=6, column=1, padx=2, pady=2, ipadx=0, ipady=0, sticky='w')

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=7, column=0, padx=2, pady=2, ipadx=0, ipady=0, columnspan=2)

        save_button = tk.Button(button_frame, text="激活", width=8, command=self.activate, bootstyle=tk.OUTLINE)
        save_button.grid(row=0, column=0, padx=10, pady=10, ipadx=0, ipady=0)

        start_button = tk.Button(button_frame, text="七天试用", width=8, command=self.seven_days_trial,
                                 bootstyle=tk.OUTLINE)
        start_button.grid(row=0, column=1, padx=10, pady=10, ipadx=0, ipady=0)

        right_down_frame = tk.Frame(self.root)
        right_down_frame.grid(row=8, column=1, padx=20, pady=2, ipadx=0, ipady=0, sticky='e')

        group_label = tk.Label(right_down_frame, text="加入讨论群", cursor="hand2", bootstyle=tk.INFO)
        group_label.grid(row=0, column=0, padx=2, pady=2, ipadx=0, ipady=0)
        group_label.bind("<Button-1>", self.open_group_link)

        join_label = tk.Label(right_down_frame, text="诚招加盟", cursor="hand2", bootstyle=tk.INFO)
        join_label.grid(row=1, column=0, padx=2, pady=2, ipadx=0, ipady=0)
        join_label.bind("<Button-1>", self.open_join_link)

    def on_id_change(self, event):
        system_setting['character_id'] = event.widget.get()
        print("人物id:", event.widget.get())

    def on_activate_code_change(self, event):
        system_setting['activate_code'] = event.widget.get()
        print("激活码:", event.widget.get())

    def activate(self):
        # TODO 根据激活码和id发送http请求判断是否激活成功
        result = True
        remaining_usage_time = 30
        if result:
            Messagebox.ok(title='激活成功', message=f'欢迎使用,剩余使用时间[{remaining_usage_time}]天\n请登录绑定游戏角色后,再次打开此程序开始使用')
            self.root.destroy()
            # for widget in self.root.winfo_children():
            #     widget.destroy()
            # applicationGui = AppilcationGui(self.root)
            # applicationGui.start_application_window()
            # print("激活成功")
        else:
            Messagebox.show_error(title='激活失败', message=f'激活失败,请检查激活码')


    def seven_days_trial(self):
        # TODO 发送http请求判断是否7天试用激活成功
        result = True
        remaining_usage_time = 7
        if result:
            Messagebox.ok(title='激活成功', message=f'欢迎试用,剩余试用时间[{remaining_usage_time}]天\n请登录绑定游戏角色后,再次打开此程序开始使用')
            self.root.destroy()
            # for widget in self.root.winfo_children():
            #     widget.destroy()
            # applicationGui = AppilcationGui(self.root)
            # applicationGui.start_application_window()
        else:
            Messagebox.show_error(title='激活失败', message=f'激活失败,请检查激活码')
    def open_group_link(self, event):
        webbrowser.open("https://www.baidu.com")

    def open_join_link(self, event):
        webbrowser.open("https://www.baidu.com")

    def on_close_activate_window(self):
        logger.info("激活窗口关闭...")
        self.root.destroy()

    def start_activate_window(self):
        self.init_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_activate_window)
        logger.info("激活窗口启动...")
        self.root.mainloop()




if __name__ == "__main__":
    root = tk.Window(themename='flatly')
    activateGui = ActivateGui(root)
    activateGui.start_activate_window()
