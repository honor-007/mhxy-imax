import webbrowser
from tkinter.messagebox import showerror, showwarning, showinfo

import ttkbootstrap as tk
from ttkbootstrap import OUTLINE
from src.utils import http_utils
from assets.sources import *
from src.utils import globalVariable

LOG_LINE_NUM = 0


class ActiveGui():

    def __init__(self, root_window):
        self.remaining_duration_label = None
        self.entry_activate_code = None
        self.start_button = None
        self.stop_button = None
        self.continue_button = None
        self.root = root_window

        # self.stop_event = threading.Event()  # 用于控制方法a的停止

    # 设置窗口
    def init_window(self):
        font = ("TkDefaultFont", 8)
        width = 16

        message_str = "    本产品需要配合kmbox硬件使用以规避游戏的键鼠检测,激活前请确认您已拥有kmbox以避免不必要浪费.kmbox购买链接:http://www.taobao.com.本产品7天试用搭配淘宝7天无理由退货,以确保您使用效果不佳不会造成任何损失."

        message = tk.Label(self.root, text=message_str, wraplength=350, font=font, bootstyle=tk.PRIMARY)
        message.grid(row=1, column=0, padx=50, pady=(20, 5), ipadx=0, ipady=0, columnspan=4)
        message_str = "声明:kmbox是第三方产品,本脚本只是借助其功能,并未与其有任何关系"
        message = tk.Label(self.root, text=message_str, wraplength=350, font=("TkDefaultFont", 10), bootstyle=tk.DANGER)
        message.grid(row=2, column=0, padx=50, pady=(5, 10), ipadx=0, ipady=0, columnspan=4)

        tk.Label(self.root, text="角色id").grid(row=3, column=0, padx=2, pady=2, ipadx=0, ipady=0)

        entry_id = tk.Entry(self.root, font=font, width=width + 2)
        entry_id.insert(0, system_setting['character_id'])
        entry_id.bind("<KeyRelease>", self.on_id_change)
        entry_id.grid(row=3, column=1, padx=2, pady=2, ipadx=0, ipady=0, sticky='w')

        tk.Label(self.root, text="剩余时间(天):").grid(row=3, column=2, padx=2, pady=2, ipadx=0, ipady=0)

        self.remaining_duration_label = tk.Label(self.root, text="0")
        self.remaining_duration_label.grid(row=3, column=3, padx=2, pady=2, ipadx=0, ipady=0)
        tk.Label(self.root, text="激活码").grid(row=4, column=0, padx=2, pady=2, ipadx=0, ipady=0, sticky='n')

        self.entry_activate_code = tk.Text(self.root, font=font, width=50, height=5)
        self.entry_activate_code.bind("<KeyRelease>", self.on_activate_code_change)
        self.entry_activate_code.grid(row=4, column=1, padx=2, pady=2, ipadx=0, ipady=0, columnspan=3, sticky='w')

        # 功能按钮
        save_button = tk.Button(self.root, text="更新ID", width=8, command=self.refresh_id, style=OUTLINE)
        save_button.grid(row=5, column=0, padx=2, pady=10, ipadx=0, ipady=0)

        self.start_button = tk.Button(self.root, text="激活", width=8, command=self.code_active,
                                      style=OUTLINE)
        self.start_button.grid(row=5, column=1, padx=2, pady=10, ipadx=0, ipady=0)

        self.stop_button = tk.Button(self.root, text="试用", width=8, command=self.trial_activate, style=OUTLINE)
        self.stop_button.grid(row=5, column=2, padx=2, pady=10, ipadx=0, ipady=0)
        # self.stop_button.config(state='disabled')

        right_down_frame = tk.Frame(self.root)
        right_down_frame.grid(row=6, column=3, padx=20, pady=2, ipadx=0, ipady=0, sticky='e')

        group_label = tk.Label(right_down_frame, text="加入讨论群", cursor="hand2", bootstyle=tk.INFO)
        group_label.grid(row=0, column=0, padx=2, pady=2, ipadx=0, ipady=0)
        group_label.bind("<Button-1>", self.open_group_link)

        join_label = tk.Label(right_down_frame, text="诚招加盟", cursor="hand2", bootstyle=tk.INFO)
        join_label.grid(row=1, column=0, padx=2, pady=2, ipadx=0, ipady=0)
        join_label.bind("<Button-1>", self.open_join_link)
        # self.continue_button = tk.Button(self.root, text="已手动处理", width=9, command=self.continue_escort_task,
        #                                  style=OUTLINE)
        # self.continue_button.grid(row=10, column=3, padx=2, pady=10, ipadx=0, ipady=0)

    def on_id_change(self, event):
        system_setting['character_id'] = event.widget.get()
        print("人物id:", event.widget.get())

    def on_activate_code_change(self, event):
        system_setting['activate_code'] = self.entry_activate_code.get("1.0", tk.END).rstrip()
        print("激活码:", system_setting['activate_code'])

    def refresh_id(self):
        write_json(system_setting, 'system_setting_json')

        check_result = http_utils.check(system_setting['character_id'])
        days = 0
        if check_result['checkResult']:
            days = check_result['remainingDuration']
            globalVariable.activate_flag = True
        else:
            globalVariable.activate_flag = False
            showerror("检查未通过", check_result['msg'])
        self.remaining_duration_label.config(text=f"{days}")

    def code_active(self):
        """
        激活码激活
        :return:
        """
        write_json(system_setting, 'system_setting_json')

        active_result = http_utils.code_activation(system_setting['activate_code'], system_setting['character_id'])
        msg = active_result['msg']
        if active_result['activeResult']:
            self.refresh_id()
            showinfo('激活成功', msg)
        else:
            showerror('激活失败', msg)

    def trial_activate(self):
        write_json(system_setting, 'system_setting_json')

        active_result = http_utils.trial_activation(system_setting['character_id'])
        msg = active_result['msg']
        if active_result['activeResult']:
            self.refresh_id()
            showinfo('激活成功', msg)
        else:
            showerror('激活失败', msg)

    def open_group_link(self, event):
        webbrowser.open("https://www.baidu.com")

    def open_join_link(self, event):
        webbrowser.open("https://www.baidu.com")
