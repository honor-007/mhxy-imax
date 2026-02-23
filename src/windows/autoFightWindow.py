import time
import threading

import ttkbootstrap as tk

import src.utils.check_util as check_util
import src.utils.globalVariable as gv
from assets.sources import auto_fight_setting, write_json
from src.components.gui_components import (
    create_combobox, create_entry, create_label_frame, create_button,
    percent_items, fkey_items, fkey_items_with_none, attack_items,
)
from src.components.window import WINDOW_ID
from src.task.autoFight import AutoFight
from src.utils.globalVariable import (
    escort_stop_event, auto_fight_stop_event, alarm_stop_event,
    stop_auto_fight_event, clear_auto_fight_event, log_queue,
    module_task_stop_event
)


class AutoFightGui():

    def __init__(self, root_window):
        self.start_button = None
        self.stop_button = None
        self.continue_button = None
        self.window = root_window

    def init_window(self):
        # ===== 人物设置 =====
        char_frame = create_label_frame(self.window, "人物设置", row=0, col=0, padx=(10, 5))

        create_entry(char_frame, 0, 0, "人物ID:", auto_fight_setting, 'character_id',
                     state='disabled', textvariable=gv.character_id)
        create_combobox(char_frame, 1, 0, "补血阈值:", percent_items(),
                        auto_fight_setting, 'character_hp_threshold')
        create_combobox(char_frame, 2, 0, "补蓝阈值:", percent_items(),
                        auto_fight_setting, 'character_mp_threshold')
        create_combobox(char_frame, 3, 0, "补充方式:", ('右键状态条', '坐骑酒肆'),
                        auto_fight_setting, 'character_restore_type')
        create_combobox(char_frame, 4, 0, "酒肆快捷键:", fkey_items(),
                        auto_fight_setting, 'stay')

        # ===== 宠物设置 =====
        pet_frame = create_label_frame(self.window, "宠物设置", row=0, col=1, padx=(5, 5))

        create_combobox(pet_frame, 0, 0, "补血阈值:", percent_items(),
                        auto_fight_setting, 'bb_hp_threshold')
        create_combobox(pet_frame, 1, 0, "补蓝阈值:", percent_items(),
                        auto_fight_setting, 'bb_mp_threshold')
        create_combobox(pet_frame, 2, 0, "补充方式:", ('右键状态条', '坐骑巫医'),
                        auto_fight_setting, 'bb_restore_type')
        create_combobox(pet_frame, 3, 0, "巫医快捷键:", fkey_items(),
                        auto_fight_setting, 'wuyi')

        # ===== 战斗设置 =====
        fight_frame = create_label_frame(self.window, "战斗设置", row=1, col=0, columnspan=2, padx=(10, 5))

        create_combobox(fight_frame, 0, 0, "打坐:", fkey_items_with_none(),
                        auto_fight_setting, 'dazuo')
        create_combobox(fight_frame, 0, 1, "人物攻击:", attack_items(),
                        auto_fight_setting, 'character_attack')
        create_combobox(fight_frame, 1, 0, "宠物攻击:", attack_items(),
                        auto_fight_setting, 'bb_attack')

        # ===== 操作按钮 =====
        btn_frame = tk.Frame(self.window)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5))

        create_button(btn_frame, "保存", self.save_auto_fight_setting,
                      row=0, col=0, bootstyle='outline-primary', padx=8)
        self.start_button = create_button(btn_frame, "开始", self.start_auto_fight_task,
                                          row=0, col=1, bootstyle='outline-success', padx=8)
        self.stop_button = create_button(btn_frame, "停止", self.end_auto_fight_task,
                                         row=0, col=2, bootstyle='outline-danger', padx=8, state='disabled')
        self.continue_button = create_button(btn_frame, "已手动处理", self.continue_auto_fight_task,
                                             row=0, col=3, bootstyle='outline-warning', padx=8)

    def start_auto_fight_task(self):
        # if not check_util.before_start_check(auto_fight_setting):
        #     return
        clear_auto_fight_event()
        self.auto_fight_thread = threading.Thread(target=self.auto_fight_task)
        self.auto_fight_thread.start()
        self.stop_button.config(state='normal')
        self.start_button.config(state='disabled')
        log_queue.put("自动战斗停止...")

    def end_auto_fight_task(self):
        stop_auto_fight_event()
        log_queue.put("结束自动战斗")
        self.stop_button.config(state='disabled')
        self.start_button.config(state='normal')

    def save_auto_fight_setting(self):
        write_json(auto_fight_setting, 'auto_fight_setting_json')
        log_queue.put("保存自动战斗配置成功")

    def continue_auto_fight_task(self):
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
        module_task_stop_event.set()
