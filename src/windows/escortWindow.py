import threading
import time

import ttkbootstrap as tk

import src.utils.globalVariable as gv
from assets.sources import escort_setting, auto_fight_setting, write_json
from src.components.gui_components import (
    create_combobox, create_entry, create_label_frame, create_button,
    percent_items, fkey_items, fkey_items_with_none, attack_items,
    FONT_SMALL, PAD_X, PAD_Y
)
from src.components.window import WINDOW_ID
from src.task.autoFight import AutoFight
from src.task.escort import escort_one_time
from src.utils import check_util
from src.utils.globalVariable import (
    escort_stop_event, auto_fight_stop_event, alarm_stop_event,
    stop_escort_event, clear_escort_event, log_queue,
    module_task_stop_event
)


class EscortGui():

    def __init__(self, root_window):
        self.start_button = None
        self.stop_button = None
        self.continue_button = None
        self.window = root_window
        self.escort_thread = None
        self.auto_fight_thread = None

    def init_window(self):
        # ===== 人物设置 =====
        char_frame = create_label_frame(self.window, "人物设置", row=0, col=0, padx=(10, 5))

        create_entry(char_frame, 0, 0, "人物ID:", escort_setting, 'character_id',
                     state='disabled', textvariable=gv.character_id)
        create_combobox(char_frame, 1, 0, "补血阈值:", percent_items(),
                        escort_setting, 'character_hp_threshold')
        create_combobox(char_frame, 2, 0, "补蓝阈值:", percent_items(),
                        escort_setting, 'character_mp_threshold')
        create_combobox(char_frame, 3, 0, "补充方式:", ('右键状态条', '坐骑酒肆'),
                        escort_setting, 'character_restore_type')
        create_combobox(char_frame, 4, 0, "酒肆快捷键:", fkey_items(),
                        escort_setting, 'stay')

        # ===== 宠物设置 =====
        pet_frame = create_label_frame(self.window, "宠物设置", row=0, col=1, padx=(5, 5))

        create_combobox(pet_frame, 0, 0, "补血阈值:", percent_items(),
                        escort_setting, 'bb_hp_threshold')
        create_combobox(pet_frame, 1, 0, "补蓝阈值:", percent_items(),
                        escort_setting, 'bb_mp_threshold')
        create_combobox(pet_frame, 2, 0, "补充方式:", ('右键状态条', '坐骑巫医'),
                        escort_setting, 'bb_restore_type')
        create_combobox(pet_frame, 3, 0, "巫医快捷键:", fkey_items(),
                        escort_setting, 'wuyi')

        # ===== 任务设置 =====
        task_frame = create_label_frame(self.window, "任务设置", row=1, col=0, padx=(10, 5))

        create_combobox(task_frame, 0, 0, "镖银等级:", ('1', '2', '3', '4'),
                        escort_setting, 'escort_level')
        create_combobox(task_frame, 1, 0, "奖励类别:", ('储备金', '现金'),
                        escort_setting, 'reward_type')

        frequency_items = tuple(str(i + 1) for i in range(50))
        create_combobox(task_frame, 2, 0, "任务次数:", frequency_items,
                        escort_setting, 'frequency')

        flag_items = (
            '红色合成旗', '黄色合成旗', '绿色合成旗', '白色合成旗', '紫色合成旗', '蓝色合成旗',
            '红色导标旗', '黄色导标旗', '绿色导标旗', '白色导标旗', '紫色导标旗', '蓝色导标旗')
        create_combobox(task_frame, 3, 0, "飞行旗:", flag_items,
                        escort_setting, 'flag_type')

        # ===== 战斗设置 =====
        fight_frame = create_label_frame(self.window, "战斗设置", row=1, col=1, padx=(5, 5))

        create_combobox(fight_frame, 0, 0, "打坐:", fkey_items_with_none(),
                        escort_setting, 'dazuo')
        create_combobox(fight_frame, 1, 0, "人物攻击:", attack_items(),
                        auto_fight_setting, 'character_attack')
        create_combobox(fight_frame, 2, 0, "宠物攻击:", attack_items(),
                        auto_fight_setting, 'bb_attack')

        # ===== 操作按钮 =====
        btn_frame = tk.Frame(self.window)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5))

        create_button(btn_frame, "保存", self.save_escort_setting,
                      row=0, col=0, bootstyle='outline-primary', padx=8)
        self.start_button = create_button(btn_frame, "开始", self.start_escort_task,
                                          row=0, col=1, bootstyle='outline-success', padx=8)
        self.stop_button = create_button(btn_frame, "停止", self.end_escort_task,
                                         row=0, col=2, bootstyle='outline-danger', padx=8, state='disabled')
        self.continue_button = create_button(btn_frame, "已手动处理", self.continue_escort_task,
                                             row=0, col=3, bootstyle='outline-warning', padx=8)

    def start_escort_task(self):
        # if not check_util.before_start_check(escort_setting):
        #     return
        clear_escort_event()
        self.escort_thread = threading.Thread(target=self.escort_task)
        self.auto_fight_thread = threading.Thread(target=self.auto_fight_task)
        self.escort_thread.start()
        self.auto_fight_thread.start()
        self.stop_button.config(state='normal')
        self.start_button.config(state='disabled')
        log_queue.put("押镖任务执行完毕...")

    def end_escort_task(self):
        stop_escort_event()
        log_queue.put("结束押镖任务")
        log_queue.put("结束自动战斗")
        self.stop_button.config(state='disabled')
        self.start_button.config(state='normal')

    def save_escort_setting(self):
        log_queue.put("保存押镖任务配置")
        write_json(escort_setting, 'escort_setting_json')

    def continue_escort_task(self):
        alarm_stop_event.set()

    def escort_task(self):
        for i in range(5):
            log_queue.put(f"脚本将在{5 - i}s后启动,请保持梦幻西游窗口在当前页面")
            time.sleep(1)
        frequency = int(escort_setting['frequency'])
        for i in range(frequency):
            if not escort_stop_event.is_set():
                log_queue.put("开始执行第[{}]次任务".format(i))
                escort_one_time()
                time.sleep(1)
            else:
                break
        module_task_stop_event.set()

    def auto_fight_task(self):
        for i in range(5):
            log_queue.put(f"自动押镖脚本将在{5 - i}s后启动,请保持梦幻西游窗口在当前页面")
            time.sleep(1)
            if escort_stop_event.is_set():
                return
        auto_fight_task = AutoFight(WINDOW_ID, escort_setting)
        while not auto_fight_stop_event.is_set():
            log_queue.put("正在执行自动战斗...")
            auto_fight_task.run()
            time.sleep(0.5)
        module_task_stop_event.set()
