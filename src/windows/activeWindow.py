import webbrowser
from tkinter.messagebox import showerror, showinfo

import ttkbootstrap as tk
from ttkbootstrap.constants import *

from assets.sources import system_setting, write_json
from src.components.gui_components import (
    create_label_frame, create_button, create_entry,
    FONT, FONT_SMALL, FONT_BOLD, PAD_X, PAD_Y
)
from src.utils import globalVariable
from src.utils import http_utils


class ActiveGui():

    def __init__(self, root_window):
        self.remaining_duration_label = None
        self.entry_activate_code = None
        self.root = root_window

    def init_window(self):
        # ===== 声明信息 =====
        info_frame = create_label_frame(self.root, "使用须知", row=0, col=0, columnspan=2, padx=10)

        message_str = "本产品需要配合kmbox硬件使用以规避游戏的键鼠检测,激活前请确认您已拥有kmbox以避免不必要浪费.kmbox购买链接:http://www.taobao.com.本产品7天试用搭配淘宝7天无理由退货,以确保您使用效果不佳不会造成任何损失."
        tk.Label(info_frame, text=message_str, wraplength=500, font=FONT_SMALL,
                 bootstyle='primary').grid(row=0, column=0, padx=10, pady=(5, 2), columnspan=4)

        tk.Label(info_frame, text="声明: kmbox是第三方产品,本脚本只是借助其功能,并未与其有任何关系",
                 wraplength=500, font=FONT_SMALL, bootstyle='danger').grid(
            row=1, column=0, padx=10, pady=(2, 8), columnspan=4)

        # ===== 激活信息 =====
        active_frame = create_label_frame(self.root, "激活信息", row=1, col=0, columnspan=2, padx=10)

        self.entry_id = create_entry(active_frame, 0, 0, "角色ID:", system_setting, 'character_id')
        # 覆盖默认绑定
        self.entry_id.unbind("<KeyRelease>")
        self.entry_id.bind("<KeyRelease>", self.on_id_change)

        tk.Label(active_frame, text="剩余时间(天):", font=FONT_SMALL).grid(
            row=0, column=2, padx=(PAD_X, 2), pady=PAD_Y, sticky='e')
        self.remaining_duration_label = tk.Label(active_frame, text="0", font=FONT_BOLD, bootstyle='success')
        self.remaining_duration_label.grid(row=0, column=3, padx=(2, PAD_X), pady=PAD_Y, sticky='w')

        tk.Label(active_frame, text="激活码:", font=FONT_SMALL).grid(
            row=1, column=0, padx=(PAD_X, 2), pady=PAD_Y, sticky='ne')
        self.entry_activate_code = tk.Text(active_frame, font=FONT_SMALL, width=45, height=4)
        self.entry_activate_code.bind("<KeyRelease>", self.on_activate_code_change)
        self.entry_activate_code.grid(row=1, column=1, padx=(2, PAD_X), pady=PAD_Y, columnspan=3, sticky='w')

        # ===== 操作按钮 =====
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5))

        create_button(btn_frame, "更新ID", self.refresh_id,
                      row=0, col=0, bootstyle='outline-primary', padx=8)
        create_button(btn_frame, "激活", self.code_active,
                      row=0, col=1, bootstyle='outline-success', padx=8)
        create_button(btn_frame, "试用", self.trial_activate,
                      row=0, col=2, bootstyle='outline-info', padx=8)

        # ===== 底部链接 =====
        link_frame = tk.Frame(self.root)
        link_frame.grid(row=3, column=1, padx=10, pady=5, sticky='e')

        group_label = tk.Label(link_frame, text="加入讨论群", cursor="hand2",
                               font=FONT_SMALL, bootstyle='info')
        group_label.grid(row=0, column=0, padx=5, pady=2)
        group_label.bind("<Button-1>", self.open_group_link)

        join_label = tk.Label(link_frame, text="诚招加盟", cursor="hand2",
                              font=FONT_SMALL, bootstyle='info')
        join_label.grid(row=0, column=1, padx=5, pady=2)
        join_label.bind("<Button-1>", self.open_join_link)

    def on_id_change(self, event):
        system_setting['character_id'] = event.widget.get()

    def on_activate_code_change(self, event):
        system_setting['activate_code'] = self.entry_activate_code.get("1.0", tk.END).rstrip()

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
