import time
import ttkbootstrap as tk
import src.utils.check_util as check_util
import src.utils.globalVariable as gv
from ttkbootstrap.constants import *
from assets.sources import windows_json, auto_fight_setting, write_json
from src.components.window import WINDOW_ID
from src.task.autoFight import AutoFight
from src.utils.globalVariable import *


class AutoFightGui():

    def __init__(self, root_window):
        self.start_button = None
        self.stop_button = None
        self.continue_button = None
        self.window = root_window

    def init_window(self):
        font = ("TkDefaultFont", 8)
        width = 16
        # 第一列内容[ "人物ID 1:","人物补血:","人物补蓝:","人物补充方式:","坐骑酒肆:","宠物补血:","宠物补蓝:","宠物补充方式:","坐骑巫医:"]
        column_1 = windows_json['auto_fight_window']["single_auto_fight_column_1"]
        for i in range(len(column_1)):
            init_data_label = tk.Label(self.window, text=column_1[i])
            init_data_label.grid(row=i, column=0, padx=2, pady=2, ipadx=0, ipady=0)

        # 第二列内容
        entry_id = tk.Entry(self.window, font=font, width=width + 2, state='disabled', textvariable=gv.character_id)
        # entry_id.insert(0, self.character_id)
        entry_id.bind("<KeyRelease>", self.on_id_change)
        entry_id.grid(row=0, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_hp = []
        for i in range(21):
            items_character_hp.append(str(i * 5) + '%')
        character_hp_threshold = tk.Combobox(self.window, font=font, width=width)
        character_hp_threshold['values'] = items_character_hp
        default_value = auto_fight_setting['character_hp_threshold']
        character_hp_threshold.current(items_character_hp.index(f'{default_value}'))
        character_hp_threshold.bind("<<ComboboxSelected>>",
                                    self.on_select_character_hp_threshold)  # 绑定事件，当下拉框选项改变时触发
        character_hp_threshold.grid(row=1, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_mp = []
        for i in range(21):
            items_character_mp.append(str(i * 5) + '%')
        character_mp_threshold = tk.Combobox(self.window, font=font, width=width)
        character_mp_threshold['values'] = items_character_mp
        default_value = auto_fight_setting['character_mp_threshold']
        character_mp_threshold.current(items_character_mp.index(f'{default_value}'))
        character_mp_threshold.bind("<<ComboboxSelected>>",
                                    self.on_select_character_mp_threshold)  # 绑定事件，当下拉框选项改变时触发
        character_mp_threshold.grid(row=2, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_restore = ('右键状态条', '坐骑酒肆')
        character_restore_type = tk.Combobox(self.window, font=font, width=width)
        character_restore_type['values'] = items_character_restore
        default_value = auto_fight_setting['character_restore_type']
        character_restore_type.current(items_character_restore.index(f'{default_value}'))
        character_restore_type.bind("<<ComboboxSelected>>",
                                    self.on_select_character_restore_type)  # 绑定事件，当下拉框选项改变时触发
        character_restore_type.grid(row=3, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_stay = ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')
        stay = tk.Combobox(self.window, font=font, width=width)
        stay['values'] = items_stay
        default_value = auto_fight_setting['stay']
        stay.current(items_stay.index(f'{default_value}'))
        stay.bind("<<ComboboxSelected>>", self.on_select_stay)  # 绑定事件，当下拉框选项改变时触发
        stay.grid(row=4, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_hp = []
        for i in range(21):
            items_bb_hp.append(str(i * 5) + '%')
        bb_hp_threshold = tk.Combobox(self.window, font=font, width=width)
        bb_hp_threshold['values'] = items_bb_hp
        default_value = auto_fight_setting['bb_hp_threshold']
        bb_hp_threshold.current(items_bb_hp.index(f'{default_value}'))
        bb_hp_threshold.bind("<<ComboboxSelected>>", self.on_select_bb_hp_threshold)  # 绑定事件，当下拉框选项改变时触发
        bb_hp_threshold.grid(row=5, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_mp = []
        for i in range(21):
            items_bb_mp.append(str(i * 5) + '%')
        bb_mp_threshold = tk.Combobox(self.window, font=font, width=width)
        bb_mp_threshold['values'] = items_bb_mp
        default_value = auto_fight_setting['bb_mp_threshold']
        bb_mp_threshold.current(items_bb_mp.index(f'{default_value}'))
        bb_mp_threshold.bind("<<ComboboxSelected>>", self.on_select_bb_mp_threshold)  # 绑定事件，当下拉框选项改变时触发
        bb_mp_threshold.grid(row=6, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_restore = ('右键状态条', '坐骑巫医')
        bb_restore_type = tk.Combobox(self.window, font=font, width=width)
        bb_restore_type['values'] = items_bb_restore
        default_value = auto_fight_setting['bb_restore_type']
        bb_restore_type.current(items_bb_restore.index(f'{default_value}'))
        bb_restore_type.bind("<<ComboboxSelected>>", self.on_select_bb_restore_type)  # 绑定事件，当下拉框选项改变时触发
        bb_restore_type.grid(row=7, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_wuyi = ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')
        wuyi = tk.Combobox(self.window, font=font, width=width)
        wuyi['values'] = items_wuyi
        default_value = auto_fight_setting['wuyi']
        wuyi.current(items_wuyi.index(f'{default_value}'))
        wuyi.bind("<<ComboboxSelected>>", self.on_select_wuyi)  # 绑定事件，当下拉框选项改变时触发
        wuyi.grid(row=8, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        # 第三列内容[ "打坐"]
        column_3 = windows_json['auto_fight_window']["single_auto_fight_column_3"]
        for i in range(len(column_3)):
            init_data_label = tk.Label(self.window, text=column_3[i])
            init_data_label.grid(row=i, column=2, padx=2, pady=2, ipadx=0, ipady=0)

        items_dazuo = ('无', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')
        dazuo = tk.Combobox(self.window, font=font, width=width)
        dazuo['values'] = items_dazuo
        default_value = auto_fight_setting['dazuo']
        dazuo.current(items_dazuo.index(f'{default_value}'))
        dazuo.bind("<<ComboboxSelected>>", self.on_select_dazuo)  # 绑定事件，当下拉框选项改变时触发
        dazuo.grid(row=0, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_attack = ('无', 'alt+q', 'alt+a', 'alt+d')
        character_attack = tk.Combobox(self.window, font=font, width=width)
        character_attack['values'] = items_character_attack
        default_value = auto_fight_setting['character_attack']
        character_attack.current(items_character_attack.index(f'{default_value}'))
        character_attack.bind("<<ComboboxSelected>>", self.on_select_character_attack)  # 绑定事件，当下拉框选项改变时触发
        character_attack.grid(row=1, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_attack = ('无', 'alt+q', 'alt+a', 'alt+d')
        bb_attack = tk.Combobox(self.window, font=font, width=width)
        bb_attack['values'] = items_bb_attack
        default_value = auto_fight_setting['bb_attack']
        bb_attack.current(items_bb_attack.index(f'{default_value}'))
        bb_attack.bind("<<ComboboxSelected>>", self.on_select_bb_attack)  # 绑定事件，当下拉框选项改变时触发
        bb_attack.grid(row=2, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        # 功能按钮
        save_button = tk.Button(self.window, text="保存", width=8, command=self.save_auto_fight_setting,
                                bootstyle=OUTLINE)
        save_button.grid(row=10, column=0, padx=2, pady=10, ipadx=0, ipady=0)

        self.start_button = tk.Button(self.window, text="开始", width=8, command=self.start_auto_fight_task,
                                      bootstyle=OUTLINE)
        self.start_button.grid(row=10, column=1, padx=2, pady=10, ipadx=0, ipady=0)

        self.stop_button = tk.Button(self.window, text="停止", width=8, command=self.end_auto_fight_task,
                                     bootstyle=OUTLINE)
        self.stop_button.grid(row=10, column=2, padx=2, pady=10, ipadx=0, ipady=0)
        self.stop_button.config(state='disabled')

        self.continue_button = tk.Button(self.window, text="已手动处理", width=9, command=self.continue_auto_fight_task,
                                         bootstyle=OUTLINE)
        self.continue_button.grid(row=10, column=3, padx=2, pady=10, ipadx=0, ipady=0)

    def on_id_change(self, event):
        auto_fight_setting['character_id'] = event.widget.get()
        print("人物id:", event.widget.get())

    def on_select_character_hp_threshold(self, event):
        auto_fight_setting['character_hp_threshold'] = event.widget.get()
        print("人物hp低于{}自动治疗".format(event.widget.get()))

    def on_select_character_mp_threshold(self, event):
        auto_fight_setting['character_mp_threshold'] = event.widget.get()
        print("人物mp低于{}自动治疗".format(event.widget.get()))

    def on_select_character_restore_type(self, event):
        auto_fight_setting['character_restore_type'] = event.widget.get()
        print("人物恢复方式:", event.widget.get())

    def on_select_bb_hp_threshold(self, event):
        auto_fight_setting['bb_hp_threshold'] = event.widget.get()
        print("宠物hp低于{}自动治疗".format(event.widget.get()))

    def on_select_bb_mp_threshold(self, event):
        auto_fight_setting['bb_mp_threshold'] = event.widget.get()
        print("宠物hp低于{}自动治疗".format(event.widget.get()))

    def on_select_bb_restore_type(self, event):
        auto_fight_setting['bb_restore_type'] = event.widget.get()
        print("宠物恢复方式:", event.widget.get())

    def on_select_stay(self, event):
        auto_fight_setting['stay'] = event.widget.get()
        print("酒肆快捷键:", event.widget.get())

    def on_select_wuyi(self, event):
        auto_fight_setting['wuyi'] = event.widget.get()
        print("巫医快捷键:", event.widget.get())

    def on_select_dazuo(self, event):
        auto_fight_setting['dazuo'] = event.widget.get()
        print("打坐:", event.widget.get())

    def on_select_character_attack(self, event):
        auto_fight_setting['character_attack'] = event.widget.get()
        print("bb攻击:", event.widget.get())

    def on_select_bb_attack(self, event):
        auto_fight_setting['bb_attack'] = event.widget.get()
        print("bb攻击:", event.widget.get())

    def start_auto_fight_task(self):
        # 1 开始前的统一检查
        if not check_util.before_start_check(auto_fight_setting):
            return
        # 2 恢复停止事件的默认设置
        clear_auto_fight_event()
        # 3 开启线程
        self.auto_fight_thread = threading.Thread(target=self.auto_fight_task)
        self.auto_fight_thread.start()

        self.stop_button.config(state='normal')  # 启用停止按钮
        self.start_button.config(state='disabled')  # 禁用开始按钮
        log_queue.put("自动战斗停止...")

    def end_auto_fight_task(self):
        stop_auto_fight_event()
        print("结束自动战斗")
        log_queue.put("结束自动战斗")
        self.stop_button.config(state='disabled')  # 启用停止按钮
        self.start_button.config(state='normal')  # 禁用开始按钮

    def save_auto_fight_setting(self):
        write_json(auto_fight_setting, 'auto_fight_setting_json')
        print("保存押镖任务配置")
        log_queue.put("保存押镖任务配置成功")

    def continue_auto_fight_task(self):
        print("继续任务")
        alarm_stop_event.set()

    def auto_fight_task(self):
        for i in range(5):
            log_queue.put(f"自动战斗脚本将在{5 - i}s后启动,请保持梦幻西游窗口在当前页面")
            time.sleep(1)
            if auto_fight_stop_event.is_set():
                return

        log_queue.put("正在执行自动战斗...")
        auto_fight_task = AutoFight(WINDOW_ID, auto_fight_setting)
        while not auto_fight_stop_event.is_set():
            auto_fight_task.run()
            time.sleep(1)
        escort_stop_event.clear()
