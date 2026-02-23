import kmNet
import ttkbootstrap as tk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip

from assets.sources import system_setting, windows_json, write_json
from src.components.gui_components import (
    create_combobox, create_entry, create_label_frame, create_button,
    FONT_SMALL, PAD_X, PAD_Y
)
from src.utils.globalVariable import log_queue
from src.utils.other_util import init_kmbox, check_ping


class SystemGui():

    def __init__(self, root_window):
        self.window = root_window
        self.entry_ip = None
        self.entry_port = None
        self.entry_uuid = None
        self.interactor_warn_one_label = None
        self.interactor_warn_two_label = None

    def init_window(self):
        # ===== 交互方式 =====
        interact_frame = create_label_frame(self.window, "交互方式", row=0, col=0, padx=10)

        interactor_combo = create_combobox(
            interact_frame, 0, 0, "交互方式:", ('模拟键鼠', '驱动键鼠'),
            system_setting, 'interactor')
        # 覆盖默认绑定，增加联动逻辑
        interactor_combo.unbind("<<ComboboxSelected>>")
        interactor_combo.bind("<<ComboboxSelected>>", self.on_select_interactor)

        warning_msg = '!此模式只可简单测试脚本功能,不可长期使用,会被检测!!!'
        self.interactor_warn_one_label = tk.Label(interact_frame, text=warning_msg[:12] + '...',
                                                  font=FONT_SMALL, bootstyle="danger")
        ToolTip(self.interactor_warn_one_label, text=warning_msg)
        self.interactor_warn_two_label = tk.Label(interact_frame, text="!此模式需设置kmbox",
                                                  font=FONT_SMALL, bootstyle="info")

        if system_setting['interactor'] == "模拟键鼠":
            self.interactor_warn_one_label.grid(row=0, column=2, padx=PAD_X, pady=PAD_Y, sticky="w")
        elif system_setting['interactor'] == "驱动键鼠":
            self.interactor_warn_two_label.grid(row=0, column=2, padx=PAD_X, pady=PAD_Y, sticky="w")

        # ===== KMBox 配置 =====
        kmbox_frame = create_label_frame(self.window, "KMBox 配置", row=1, col=0, padx=10)

        km_state = 'normal' if system_setting['interactor'] == '驱动键鼠' else 'disabled'
        self.entry_ip = create_entry(kmbox_frame, 0, 0, "IP 地址:", system_setting, 'IP', state=km_state)
        self.entry_port = create_entry(kmbox_frame, 1, 0, "端口:", system_setting, 'Port', state=km_state)
        self.entry_uuid = create_entry(kmbox_frame, 2, 0, "UUID:", system_setting, 'UUID', state=km_state)

        # ===== 操作按钮 =====
        btn_frame = tk.Frame(self.window)
        btn_frame.grid(row=2, column=0, pady=(10, 5))

        create_button(btn_frame, "保存", self.save_system_setting,
                      row=0, col=0, bootstyle='outline-primary', padx=8)
        create_button(btn_frame, "测试kmbox", self.test_kmbox_connect,
                      row=0, col=1, bootstyle='outline-info', padx=8)

        # 提示信息
        tk.Label(self.window, text="注意: 修改配置后需点击保存，然后重启才能生效",
                 font=FONT_SMALL, bootstyle="danger").grid(
            row=3, column=0, padx=10, pady=(10, 5))

    def on_select_interactor(self, event):
        system_setting['interactor'] = event.widget.get()
        if event.widget.get() == "模拟键鼠":
            self.interactor_warn_two_label.grid_forget()
            self.interactor_warn_one_label.grid(row=0, column=2, padx=PAD_X, pady=PAD_Y, sticky="w")
            self.entry_ip.config(state='disabled')
            self.entry_port.config(state='disabled')
            self.entry_uuid.config(state='disabled')
        elif event.widget.get() == "驱动键鼠":
            self.interactor_warn_one_label.grid_forget()
            self.interactor_warn_two_label.grid(row=0, column=2, padx=PAD_X, pady=PAD_Y, sticky="w")
            self.entry_ip.config(state='normal')
            self.entry_port.config(state='normal')
            self.entry_uuid.config(state='normal')

    def save_system_setting(self):
        log_queue.put("保存系统设置")
        write_json(system_setting, 'system_setting_json')

    def test_kmbox_connect(self):
        if not check_ping(system_setting['IP']):
            Messagebox.show_warning(title='警告', message='kmbox无法ping通,请在系统设置中修正kmbox相关参数配置')
            return False
        result = kmNet.init(system_setting['IP'], system_setting['Port'], system_setting['UUID'])
        if result == 0:
            Messagebox.show_info(title="kmbox连接测试", message="成功连接到kmbox！")
            return True
        else:
            Messagebox.show_warning(title='警告', message='kmbox无法连接,请在系统设置中修正kmbox相关参数配置')
            return False
