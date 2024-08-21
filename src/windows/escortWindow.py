import threading
import time
import ttkbootstrap as tk
from ttkbootstrap import OUTLINE

# from ttkbootstrap import *

from src.components.window import WINDOW_ID
from src.modules.autoFight import AutoFight
from src.task.escort import escort_one_time
from src.utils.globalVariable import escort_stop_event, auto_fight_stop_event,  alarm_stop_event, \
    stop_escort_event, clear_escort_event
from assets.sources import *
from src.utils.log_util import log_queue

LOG_LINE_NUM = 0


class EscortGui():

    def __init__(self, root_window):
        self.start_button = None
        self.stop_button = None
        self.continue_button = None
        self.window = root_window

        self.escort_thread = None
        self.auto_fight_thread = None
        # self.stop_event = threading.Event()  # 用于控制方法a的停止

    # 设置窗口
    def init_window(self):
        font = ("TkDefaultFont", 8)
        width = 16
        # 第一列内容[ "人物ID 1:","镖银等级:","奖励类别:","人物补血:","人物补蓝:","人物补充方式:","坐骑酒肆:","宠物补血:","宠物补蓝:","宠物补充方式:","坐骑巫医:"]
        column_1 = windows_json['escort_window']["single_escort_column_1"]
        for i in range(len(column_1)):
            init_data_label = tk.Label(self.window, text=column_1[i])
            init_data_label.grid(row=i, column=0, padx=2, pady=2, ipadx=0, ipady=0)

        # 第二列内容
        entry_id = tk.Entry(self.window, font=font, width=width + 2)
        entry_id.insert(0, escort_setting['character_id'])
        entry_id.bind("<KeyRelease>", self.on_id_change)
        entry_id.grid(row=0, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_escort_level = ('1', '2', '3', '4')
        escort_level = tk.Combobox(self.window, font=font, width=width)
        escort_level['values'] = items_escort_level
        default_value = escort_setting['escort_level']
        escort_level.current(items_escort_level.index(f'{default_value}'))
        escort_level.bind("<<ComboboxSelected>>", self.on_select_escort_level)  # 绑定事件，当下拉框选项改变时触发
        escort_level.grid(row=1, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_reward_type = ('储备金', '现金')
        reward_type = tk.Combobox(self.window, font=font, width=width)
        reward_type['values'] = items_reward_type
        default_value = escort_setting['reward_type']
        reward_type.current(items_reward_type.index(f'{default_value}'))
        reward_type.bind("<<ComboboxSelected>>", self.on_select_reward_type)  # 绑定事件，当下拉框选项改变时触发
        reward_type.grid(row=2, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_hp = ('0%', '25%', '50%', '75%', '80%', '90%')
        character_hp_threshold = tk.Combobox(self.window, font=font, width=width)
        character_hp_threshold['values'] = items_character_hp
        default_value = escort_setting['character_hp_threshold']
        character_hp_threshold.current(items_character_hp.index(f'{default_value}'))
        character_hp_threshold.bind("<<ComboboxSelected>>", self.on_select_character_hp_threshold)  # 绑定事件，当下拉框选项改变时触发
        character_hp_threshold.grid(row=3, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_mp = ('0%', '25%', '50%', '75%', '80%', '90%')
        character_mp_threshold = tk.Combobox(self.window, font=font, width=width)
        character_mp_threshold['values'] = items_character_mp
        default_value = escort_setting['character_mp_threshold']
        character_mp_threshold.current(items_character_mp.index(f'{default_value}'))
        character_mp_threshold.bind("<<ComboboxSelected>>", self.on_select_character_mp_threshold)  # 绑定事件，当下拉框选项改变时触发
        character_mp_threshold.grid(row=4, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_restore = ('右键状态条', '坐骑酒肆')
        character_restore_type = tk.Combobox(self.window, font=font, width=width)
        character_restore_type['values'] = items_character_restore
        default_value = escort_setting['character_restore_type']
        character_restore_type.current(items_character_restore.index(f'{default_value}'))
        character_restore_type.bind("<<ComboboxSelected>>", self.on_select_character_restore_type)  # 绑定事件，当下拉框选项改变时触发
        character_restore_type.grid(row=5, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_stay = ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')
        stay = tk.Combobox(self.window, font=font, width=width)
        stay['values'] = items_stay
        default_value = escort_setting['stay']
        stay.current(items_stay.index(f'{default_value}'))
        stay.bind("<<ComboboxSelected>>", self.on_select_stay)  # 绑定事件，当下拉框选项改变时触发
        stay.grid(row=6, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_hp = ('0%', '25%', '50%', '75%', '80%', '90%')
        bb_hp_threshold = tk.Combobox(self.window, font=font, width=width)
        bb_hp_threshold['values'] = items_bb_hp
        default_value = escort_setting['bb_hp_threshold']
        bb_hp_threshold.current(items_bb_hp.index(f'{default_value}'))
        bb_hp_threshold.bind("<<ComboboxSelected>>", self.on_select_bb_hp_threshold)  # 绑定事件，当下拉框选项改变时触发
        bb_hp_threshold.grid(row=7, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_mp = ('0%', '25%', '50%', '75%', '80%', '90%')
        bb_mp_threshold = tk.Combobox(self.window, font=font, width=width)
        bb_mp_threshold['values'] = items_bb_mp
        default_value = escort_setting['bb_mp_threshold']
        bb_mp_threshold.current(items_bb_mp.index(f'{default_value}'))
        bb_mp_threshold.bind("<<ComboboxSelected>>", self.on_select_bb_mp_threshold)  # 绑定事件，当下拉框选项改变时触发
        bb_mp_threshold.grid(row=8, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_restore = ('右键状态条', '坐骑巫医')
        bb_restore_type = tk.Combobox(self.window, font=font, width=width)
        bb_restore_type['values'] = items_bb_restore
        default_value = escort_setting['bb_restore_type']
        bb_restore_type.current(items_bb_restore.index(f'{default_value}'))
        bb_restore_type.bind("<<ComboboxSelected>>", self.on_select_bb_restore_type)  # 绑定事件，当下拉框选项改变时触发
        bb_restore_type.grid(row=9, column=1, padx=2, pady=2, ipadx=0, ipady=0)

        # 第三列内容[ "人物ID 1:","镖银等级:","奖励类别:","人物补血:","人物补蓝:","人物补充方式:","坐骑酒肆:","宠物补血:","宠物补蓝:","宠物补充方式:","坐骑巫医:"]
        column_3 = windows_json['escort_window']["single_escort_column_3"]
        for i in range(len(column_3)):
            init_data_label = tk.Label(self.window, text=column_3[i])
            init_data_label.grid(row=i, column=2, padx=2, pady=2, ipadx=0, ipady=0)

        # 第四列内容
        items_wuyi = ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')
        wuyi = tk.Combobox(self.window, font=font, width=width)
        wuyi['values'] = items_wuyi
        default_value = escort_setting['wuyi']
        wuyi.current(items_wuyi.index(f'{default_value}'))
        wuyi.bind("<<ComboboxSelected>>", self.on_select_wuyi)  # 绑定事件，当下拉框选项改变时触发
        wuyi.grid(row=0, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        items_frequency = []
        for i in range(50):
            items_frequency.append(str(i + 1))
        frequency = tk.Combobox(self.window, font=font, width=width)
        frequency['values'] = items_frequency
        default_value = escort_setting['frequency']
        frequency.current(items_frequency.index(f'{default_value}'))
        frequency.bind("<<ComboboxSelected>>", self.on_select_frequency)  # 绑定事件，当下拉框选项改变时触发
        frequency.grid(row=1, column=3, padx=2, pady=2, ipadx=0, ipady=0)
        items_flag_type = (
            '红色合成旗', '黄色合成旗', '绿色合成旗', '白色合成旗', '紫色合成旗', '蓝色合成旗', '红色导标旗',
            '黄色导标旗',
            '绿色导标旗',
            '白色导标旗', '紫色导标旗', '蓝色导标旗',)
        flag_type = tk.Combobox(self.window, font=font, width=width)
        flag_type['values'] = items_flag_type
        default_value = escort_setting['flag_type']
        flag_type.current(items_flag_type.index(f'{default_value}'))
        flag_type.bind("<<ComboboxSelected>>", self.on_select_flag_type)  # 绑定事件，当下拉框选项改变时触发
        flag_type.grid(row=2, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        items_dazuo = ('无', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9')
        dazuo = tk.Combobox(self.window, font=font, width=width)
        dazuo['values'] = items_dazuo
        default_value = escort_setting['dazuo']
        dazuo.current(items_dazuo.index(f'{default_value}'))
        dazuo.bind("<<ComboboxSelected>>", self.on_select_dazuo)  # 绑定事件，当下拉框选项改变时触发
        dazuo.grid(row=3, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        items_character_attack = ('无', 'alt+q', 'alt+a')
        character_attack = tk.Combobox(self.window, font=font, width=width)
        character_attack['values'] = items_character_attack
        default_value = auto_fight_setting['character_attack']
        character_attack.current(items_character_attack.index(f'{default_value}'))
        character_attack.bind("<<tk.ComboboxSelected>>", self.on_select_character_attack)  # 绑定事件，当下拉框选项改变时触发
        character_attack.grid(row=4, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        items_bb_attack = ('无', 'alt+q', 'alt+a')
        bb_attack = tk.Combobox(self.window, font=font, width=width)
        bb_attack['values'] = items_bb_attack
        default_value = auto_fight_setting['bb_attack']
        bb_attack.current(items_bb_attack.index(f'{default_value}'))
        bb_attack.bind("<<tk.ComboboxSelected>>", self.on_select_bb_attack)  # 绑定事件，当下拉框选项改变时触发
        bb_attack.grid(row=5, column=3, padx=2, pady=2, ipadx=0, ipady=0)

        # 功能按钮
        save_button = tk.Button(self.window, text="保存", width=8, command=self.save_escort_setting, style=OUTLINE)
        save_button.grid(row=10, column=0, padx=2, pady=10, ipadx=0, ipady=0)

        self.start_button = tk.Button(self.window, text="开始", width=8, command=self.start_escort_task,
                                      style=OUTLINE)
        self.start_button.grid(row=10, column=1, padx=2, pady=10, ipadx=0, ipady=0)

        self.stop_button = tk.Button(self.window, text="停止", width=8, command=self.end_escort_task, style=OUTLINE)
        self.stop_button.grid(row=10, column=2, padx=2, pady=10, ipadx=0, ipady=0)
        self.stop_button.config(state='disabled')

        self.continue_button = tk.Button(self.window, text="已手动处理", width=9, command=self.continue_escort_task,
                                         style=OUTLINE)
        self.continue_button.grid(row=10, column=3, padx=2, pady=10, ipadx=0, ipady=0)

    def on_id_change(self, event):
        escort_setting['character_id'] = event.widget.get()
        print("人物id:", event.widget.get())

    def on_select_escort_level(self, event):
        escort_setting['escort_level'] = event.widget.get()
        print("镖银等级:", event.widget.get())

    def on_select_reward_type(self, event):
        escort_setting['reward_type'] = event.widget.get()
        print("任务奖励选择:", event.widget.get())

    def on_select_character_hp_threshold(self, event):
        escort_setting['character_hp_threshold'] = event.widget.get()
        print("人物hp低于{}自动治疗".format(event.widget.get()))

    def on_select_character_mp_threshold(self, event):
        escort_setting['character_mp_threshold'] = event.widget.get()
        print("人物mp低于{}自动治疗".format(event.widget.get()))

    def on_select_character_restore_type(self, event):
        escort_setting['character_restore_type'] = event.widget.get()
        print("人物恢复方式:", event.widget.get())

    def on_select_bb_hp_threshold(self, event):
        escort_setting['bb_hp_threshold'] = event.widget.get()
        print("宠物hp低于{}自动治疗".format(event.widget.get()))

    def on_select_bb_mp_threshold(self, event):
        escort_setting['bb_mp_threshold'] = event.widget.get()
        print("宠物hp低于{}自动治疗".format(event.widget.get()))

    def on_select_bb_restore_type(self, event):
        escort_setting['bb_restore_type'] = event.widget.get()
        print("宠物恢复方式:", event.widget.get())

    def on_select_stay(self, event):
        escort_setting['stay'] = event.widget.get()
        print("酒肆快捷键:", event.widget.get())

    def on_select_wuyi(self, event):
        escort_setting['wuyi'] = event.widget.get()
        print("巫医快捷键:", event.widget.get())

    def on_select_frequency(self, event):
        escort_setting['frequency'] = event.widget.get()
        print("任务次数:", event.widget.get())

    def on_select_flag_type(self, event):
        escort_setting['flag_type'] = event.widget.get()
        print("镖局飞行旗颜色:", event.widget.get())

    def on_select_dazuo(self, event):
        escort_setting['dazuo'] = event.widget.get()
        print("打坐:", event.widget.get())

    def on_select_character_attack(self, event):
        auto_fight_setting['character_attack'] = event.widget.get()
        print("bb攻击:", event.widget.get())

    def on_select_bb_attack(self, event):
        auto_fight_setting['bb_attack'] = event.widget.get()
        print("bb攻击:", event.widget.get())
    def start_escort_task(self):
        print("开始执行任务")
        for key, value in escort_setting.items():
            if value is None:
                log_queue.put("{}设置内容有缺失,无法启动(不使用坐骑技能请随便设置,不可为空)".format(key))
                print("{}设置内容有缺失,无法启动(不使用坐骑技能请随便设置,不可为空)".format(key))
                return
        clear_escort_event()
        self.escort_thread = threading.Thread(target=self.escort_task)
        self.auto_fight_thread = threading.Thread(target=self.auto_fight_task)
        self.escort_thread.start()
        self.auto_fight_thread.start()

        self.stop_button.config(state='normal')  # 启用停止按钮
        self.start_button.config(state='disabled')  # 禁用开始按钮

        print("押镖任务执行完毕")

    def end_escort_task(self):
        stop_escort_event()
        log_queue.put("结束押镖任务")
        log_queue.put("结束自动战斗")
        self.stop_button.config(state='disabled')  # 启用停止按钮
        self.start_button.config(state='normal')  # 禁用开始按钮

    def save_escort_setting(self):
        print("保存押镖任务配置")
        log_queue.put("保存押镖任务配置")
        write_json(escort_setting, 'escort_setting_json')

    def continue_escort_task(self):
        print("继续任务")
        alarm_stop_event.set()

    def escort_task(self):
        for i in range(5):
            log_queue.put(f"脚本将在{5 - i}s后启动,请保持梦幻西游窗口在当前页面")
            time.sleep(1)

        frequency = int(escort_setting['frequency'])
        for i in range(frequency):
            if not escort_stop_event.is_set():
                log_queue.put("开始执行第[{}]次任务".format(i))
                print("开始执行第[{}]次任务".format(i))
                escort_one_time()
                time.sleep(1)
            else:
                break
        escort_stop_event.clear()

    def auto_fight_task(self):
        for i in range(5):
            log_queue.put(f"自动押镖脚本将在{5 - i}s后启动,请保持梦幻西游窗口在当前页面")
            time.sleep(1)
        auto_fight_task = AutoFight(WINDOW_ID, escort_setting)
        while not auto_fight_stop_event.is_set():
            log_queue.put("正在执行自动战斗...")
            auto_fight_task.run()
            time.sleep(1)
        auto_fight_stop_event.clear()
