from ttkbootstrap import *
import ttkbootstrap as tk

from assets.sources import activate_setting


class activateGui(tk.Window):
    """
    激活窗口
    """

    def __init__(self):
        super().__init__()
        Style(theme='flatly')

        self.title("MHXY 辅助工具 v1.0")  # 窗口名
        self.geometry('600x450+10+10')  # 290 160为窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.iconbitmap(r'')
        self.iconbitmap(r'../../assets/assets/icon.ico')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        width = 32
        font = ("TkDefaultFont", 12)

        message_str = "欢迎使用!"
        title = tk.Label(self, text=message_str, wraplength=500, font=("TkDefaultFont", 12, 'bold'))
        title.grid(row=0, column=0, padx=50, pady=(40, 0), ipadx=0, ipady=0, columnspan=2)

        message_str = "    本产品需要配合kmbox硬件使用以规避游戏的键鼠检测,激活前请确认您已拥有kmbox以避免不必要浪费.kmbox购买链接:http://www.taobao.com.本产品7天试用搭配淘宝7天无理由退货,以确保您使用效果不佳不会造成任何损失."

        message = tk.Label(self, text=message_str, wraplength=500, font=font, bootstyle="default")
        message.grid(row=1, column=0, padx=50, pady=(20, 5), ipadx=0, ipady=0, columnspan=2)
        message_str = "声明:kmbox是第三方产品,本脚本只是借助其功能,并未与其有任何关系"
        message = tk.Label(self, text=message_str, wraplength=500, font=("TkDefaultFont", 10), bootstyle="danger")
        message.grid(row=2, column=0, padx=50, pady=(5, 10), ipadx=0, ipady=0, columnspan=2)

        id_label = tk.Label(self, text='角色ID:')
        id_label.grid(row=5, column=0, padx=2, pady=2, ipadx=0, ipady=0, sticky='e')

        entry_id = tk.Entry(self, font=font, width=width + 2)
        entry_id.bind("<KeyRelease>", self.on_id_change)
        entry_id.grid(row=5, column=1, padx=2, pady=2, ipadx=0, ipady=0, sticky='w')

        activate_code_label = tk.Label(self, text='激活码:')
        activate_code_label.grid(row=6, column=0, padx=2, pady=2, ipadx=0, ipady=0, sticky='en')

        entry_activate_code = tk.Text(self, font=font, width=width + 2, height=5)
        entry_activate_code.bind("<KeyRelease>", self.on_activate_code_change)
        entry_activate_code.grid(row=6, column=1, padx=2, pady=2, ipadx=0, ipady=0, sticky='w')

        button_frame = tk.Frame(self)
        button_frame.grid(row=7, column=0, padx=2, pady=2, ipadx=0, ipady=0, columnspan=2)

        save_button = tk.Button(button_frame, text="激活", width=8, command=self.activate, bootstyle=OUTLINE)
        save_button.grid(row=7, column=0, padx=10, pady=10, ipadx=0, ipady=0)

        self.start_button = tk.Button(button_frame, text="七天试用", width=8, command=self.seven_days_trial,
                                      bootstyle=OUTLINE)
        self.start_button.grid(row=7, column=1, padx=10, pady=10, ipadx=0, ipady=0)

    def on_id_change(self, event):
        activate_setting['character_id'] = event.widget.get()
        print("人物id:", event.widget.get())

    def on_activate_code_change(self, event):
        activate_setting['activate_code'] = event.widget.get()
        print("激活码:", event.widget.get())

    def activate(self):
        print("激活成功")

    def seven_days_trial(self):
        print("试用激活成功")


activateGui = activateGui()
activateGui.mainloop()
