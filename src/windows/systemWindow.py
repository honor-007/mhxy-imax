import kmNet
import ttkbootstrap as tk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip

from assets.sources import system_setting, windows_json, write_json
from src.utils.log_util import log_queue


class SystemGui():

    def __init__(self, root_window):
        self.window = root_window

    def init_window(self):
        font = ("TkDefaultFont", 8)
        width = 16

        # 第一列内容[]
        column_1 = windows_json['system_window']["single_system_column_1"]
        for i in range(len(column_1)):
            init_data_label = tk.Label(self.window, text=column_1[i])
            init_data_label.grid(row=i, column=0, padx=2, pady=2, ipadx=0, ipady=0)

        items_interactor_restore = ('模拟键鼠', '驱动键鼠')
        interactor_gui = tk.Combobox(self.window, font=font, width=width)
        interactor_gui['values'] = items_interactor_restore
        default_value = system_setting['interactor']
        interactor_gui.current(items_interactor_restore.index(f'{default_value}'))
        interactor_gui.bind("<<ComboboxSelected>>", self.on_select_interactor)  # 绑定事件，当下拉框选项改变时触发
        interactor_gui.grid(row=0, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        self.entry_ip = tk.Entry(self.window, font=font, width=width + 2)
        self.entry_ip.insert(0, system_setting['IP'])
        self.entry_ip.bind("<KeyRelease>", self.on_ip_change)
        self.entry_ip.grid(row=1, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        self.entry_port = tk.Entry(self.window, font=font, width=width + 2)
        self.entry_port.insert(0, system_setting['Port'])
        self.entry_port.bind("<KeyRelease>", self.on_port_change)
        self.entry_port.grid(row=2, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        self.entry_uuid = tk.Entry(self.window, font=font, width=width + 2)
        self.entry_uuid.insert(0, system_setting['UUID'])
        self.entry_uuid.bind("<KeyRelease>", self.on_uuid_change)
        self.entry_uuid.grid(row=3, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        waring_message = '!此模式只可简单测试脚本功能,不可长期使用,会被检测!!!'
        self.interactor_warn_one_label = tk.Label(self.window,
                                                  text=waring_message[:10] + '...',
                                                  bootstyle="danger")
        ToolTip(self.interactor_warn_one_label, text=waring_message)
        self.interactor_warn_two_label = tk.Label(self.window, text="!此模式需设置kmbox", bootstyle="info")
        if system_setting['interactor'] == "模拟键鼠":
            self.interactor_warn_one_label.grid(row=0, column=2, padx=2, pady=2, ipadx=0, ipady=0)
        if system_setting['interactor'] == "驱动键鼠":
            self.interactor_warn_two_label.grid(row=0, column=2, padx=2, pady=2, ipadx=0, ipady=0)

        # 功能按钮
        save_button = tk.Button(self.window, text="保存", width=8, command=self.save_system_setting, style=OUTLINE)
        save_button.grid(row=10, column=0, padx=2, pady=10, ipadx=0, ipady=0)

        save_button = tk.Button(self.window, text="测试kmbox", width=8, command=self.test_kmbox_connect, style=OUTLINE)
        save_button.grid(row=10, column=1, padx=2, pady=10, ipadx=0, ipady=0)

        self.system_warning_label = tk.Label(self.window, text="注意:修改配置后,需要点击保存,然后重启才能生效",
                                             bootstyle="danger")
        self.system_warning_label.grid(row=12, column=0, padx=2, pady=10, ipadx=0, ipady=0, columnspan=3)
    def on_select_interactor(self, event):
        system_setting['interactor'] = event.widget.get()
        print("gui交互方式:", event.widget.get())
        if event.widget.get() == "模拟键鼠":
            self.interactor_warn_two_label.grid_forget()
            self.interactor_warn_one_label.grid(row=0, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky="w")
            self.entry_ip.config(state='disabled')
            self.entry_port.config(state='disabled')
            self.entry_uuid.config(state='disabled')
        elif event.widget.get() == "驱动键鼠":
            self.interactor_warn_one_label.grid_forget()
            self.interactor_warn_two_label.grid(row=0, column=2, padx=2, pady=2, ipadx=0, ipady=0, sticky="w")
            self.entry_ip.config(state='normal')
            self.entry_port.config(state='normal')
            self.entry_uuid.config(state='normal')

    def on_ip_change(self, event):
        system_setting['IP'] = event.widget.get()
        print("kmbox_IP:", event.widget.get())

    def on_port_change(self, event):
        system_setting['Port'] = event.widget.get()
        print("kmbox_Port:", event.widget.get())

    def on_uuid_change(self, event):
        system_setting['UUID'] = event.widget.get()
        print("kmbox_UUID:", event.widget.get())

    def save_system_setting(self):
        print("保存系统设置")
        log_queue.put("保存系统设置")
        write_json(system_setting, 'escort_setting_json')

    def test_kmbox_connect(self):
        result = kmNet.init(system_setting['IP'], system_setting['Port'], system_setting['UUID'])
        if result == 0:
            Messagebox.show_info("成功连接到kmbox！", "kmbox连接测试")
        else:
            Messagebox.show_error("连接kmbox失败,请检查ip,port,uuid是否正确！", "kmbox连接测试")
