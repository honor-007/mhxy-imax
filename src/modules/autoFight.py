# -*- coding: gbk -*-
import threading
from datetime import datetime
import time
import random
import pywintypes
import win32gui
import game_models.hoverModel as hm
from assets.sources import get_source, auto_fight_setting
from config import hover_list
from game_models.roleModel import get_role_center
from script_utils.imageTransform import get_hp_rect, get_mp_rect
from src.components.hover import hover
from src.components.status import isFight
from src.components.gameMouse import game_mouse
from src.components.InputAutoGui import inputautogui
from src.components.window import WINDOW_ID
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img, crop_image_data
from src.modules.map import click_button
from src.utils import sound_util
from src.utils.globalVariable import alarm_stop_event, auto_fight_stop_event, dazuo_stop_event
from src.utils.log_util import log_queue
from src.utils.random_util import random_button_coordinate
from script_utils.cnOcr import cn_ocr


class AutoFight:
    def __init__(self, hwnd, auto_fight_setting):
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)
        self.dazuo_thread_is_running = False
        self.auto_fight_setting = auto_fight_setting

    def __screenshot(self):
        return winShot(self.hwnd)

    def __task(self, fight_type=0, rate=0.85):
        if not self.__windows_in_screen():
            return False
        if fight_type == 0:
            if hover.normalNotification(rate):
                logger.info("存在弹窗：切割完毕")
                return True
        elif fight_type == 1:
            if hover.rewardNotification(rate):
                logger.info("存在奖励弹窗：切割完毕")
                return True
        return False

    def __windows_in_screen(self):
        """
        判断当前窗口是否是mhxy的窗口
        :return:
        """
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name

    def __auto_click_four_people(self, fight_type=0, rate=0.85):
        """
        !!!自动处理弹窗
        :param fight_type:
        :param rate:
        :return:
        """
        if isFight.is_fighting():
            log_queue.put("战斗中,检查并处理奖励弹窗")
            # 有弹窗并完成切割返回true 否则false
            if not self.__task(fight_type, rate):
                return
            min_index = hm.model_predict(hover_list)
            result = match_img(self.__screenshot(), hover_list[min_index], 10, 10, 0.98)
            if result[3] is None:
                return
            target_x, target_y = result[3]['result']

            # 利用yolo5 检测出头部
            xcenter, ycenter = get_role_center(hover_list[min_index])
            target_x = target_x + xcenter - 45
            target_y = target_y + ycenter - 70

            log_queue.put(f' 点击坐标为 > x：{target_x} < ; y：{target_y}')
            if target_x == 0 and target_y == 0:
                while not alarm_stop_event.is_set():
                    sound_util.playsound()
                    log_queue.put("匹配失败弹窗点击失败,需要手动处理")
                alarm_stop_event.clear()
            else:
                log_queue.put("开始点击弹窗")
                game_mouse.move_click(target_x, target_y)
                time.sleep(0.5)
                if hover.secondNotification(rate):
                    min_index = hm.model_predict(hover_list)
                    result = match_img(self.__screenshot(), hover_list[min_index], 10, 10, 0.98)
                    if result[3] is None:
                        return
                    target_x, target_y = result[3]['result']

                    # 利用yolo5 检测出头部
                    xcenter, ycenter = get_role_center(hover_list[min_index])
                    target_x = target_x + xcenter - 45
                    target_y = target_y + ycenter - 70

                    if target_x == 0 and target_y == 0:
                        logger.warning('匹配失败弹窗点击失败')
                    else:
                        game_mouse.move_click(target_x, target_y)
        else:
            # 非战斗中的处理
            # 恢复
            log_queue.put("非战斗中,检查人物状态")
            self.restore()

            if not self.dazuo_thread_is_running and self.auto_fight_setting['dazuo'] != '无':
                dazuo_thread = threading.Thread(target=self.dazuo())
                dazuo_thread.start()

    def __auto_action(self):
        """
        攻击操作
        :return:
        """
        if isFight.is_fighting():
            log_queue.put("战斗中,弹窗处理完毕,执行战斗操作")
            if isFight.is_need_fight_action():
                if self.auto_fight_setting["character_attack"] == "alt+a":
                    inputautogui.hotkey('alt', 'a')
                elif self.auto_fight_setting["character_attack"] == "alt+q":
                    inputautogui.hotkey('alt', 'q')
                time.sleep(random.randint(0, 5) / 10)
                if self.auto_fight_setting["bb_attack"] == "alt+a":
                    inputautogui.hotkey('alt', 'a')
                elif self.auto_fight_setting["bb_attack"] == "alt+q":
                    inputautogui.hotkey('alt', 'q')
            return True
        return False

    def __handle_click(self, fight_type=0, rate=0.85):
        """
        !!!手动处理弹窗(遇到弹窗时发出报警声音)
        :return:
        """
        if isFight.is_fighting():
            # 判断是否有弹窗
            if not self.__task(fight_type, rate):
                return
            # 发出报警声音 等待处理
            while not alarm_stop_event.is_set():
                sound_util.playsound()
                print("出现弹窗,需要手动处理")
            alarm_stop_event.clear()
        else:
            # 非战斗中的处理
            # 恢复
            log_queue.put("非战斗状态操作")
            self.restore()

            if not self.dazuo_thread_is_running and self.auto_fight_setting['dazuo'] != '无':
                dazuo_thread = threading.Thread(target=self.dazuo())
                dazuo_thread.start()
            time.sleep(5)

    def dazuo(self):
        self.dazuo_thread_is_running = True
        while not dazuo_stop_event.is_set():
            log_queue.put("打坐回蓝...")
            inputautogui.press(self.auto_fight_setting['dazuo'])
            time.sleep(random.randint(90, 150))
        self.dazuo_thread_is_running = False

    def restore(self):
        log_queue.put("检查人物和bb状态是否需要恢复")
        img = self.__screenshot()
        state_width = 50
        # 截取人物状态栏
        character_img = crop_image_data(img, (955, 0), (1020, 50))

        # x, y, w, h = get_hp_rect(character_img)
        result = get_hp_rect(character_img)
        if result is not None and result[2] > 0:
            # log_queue.put("人物hp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            character_hp_rate = round(result[2] / state_width * 100)
            # log_queue.put(" character_hp_rate:{}".format(character_hp_rate))
            if character_hp_rate <= int(self.auto_fight_setting["character_hp_threshold"][:-1]):
                # log_queue.put(
                #     f'人物气血百分比{character_hp_rate},小于{self.auto_fight_setting["character_hp_threshold"]},需要执行加血指令')
                self.restore_character_hp_command()
        else:
            log_queue.put("未读取到人物hp,不做操作")

        # x, y, w, h = get_mp_rect(character_img)
        result = get_mp_rect(character_img)
        if result is not None and result[2] > 0:
            # log_queue.put("人物mp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            character_mp_rate = round(result[2] / state_width * 100)
            # log_queue.put(" character_mp_rate:{}".format(character_mp_rate))
            if character_mp_rate <= int(self.auto_fight_setting["character_mp_threshold"][:-1]):
                # log_queue.put(
                #     f'人物魔法百分比:{character_mp_rate},小于{self.auto_fight_setting["character_mp_threshold"]},需要执行加蓝指令')
                self.restore_character_mp_command()
        else:
            log_queue.put("未读取到人物mp,不做操作")

        bb_img = crop_image_data(img, (845, 0), (900, 50))
        result = get_hp_rect(bb_img)
        if result is not None and result[2] > 0:
            # log_queue.put("宠物hp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            bb_hp_rate = round(result[2] / state_width)
            if bb_hp_rate <= int(self.auto_fight_setting["bb_hp_threshold"][:-1]):
                # log_queue.put(
                #     f'bb气血百分比:{bb_hp_rate},小于{self.auto_fight_setting["bb_hp_threshold"]},需要执行加血指令')

                self.restore_bb_hp_command()
        else:
            log_queue.put("未读取到宠物hp,不做操作")

        # x, y, w, h = get_mp_rect(bb_img)
        result = get_mp_rect(bb_img)
        if result is not None and result[2] > 0:
            # log_queue.put("宠物mp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            bb_mp_rate = round(result[2] / state_width)
            if bb_mp_rate <= int(self.auto_fight_setting["bb_mp_threshold"][:-1]):
                # log_queue.put(
                #     f'bb魔法百分比:{bb_mp_rate},小于{self.auto_fight_setting["bb_mp_threshold"]},需要执行加蓝指令')
                self.restore_bb_mp_command()
        else:
            log_queue.put("未读取到宠物mp,不做操作")

    def restore_character_hp_command(self):
        if '右键状态条' == self.auto_fight_setting['character_restore_type']:
            # 如果是右键恢复前先检查是否有对话框并处理
            self.click_dialog()
            game_mouse.move_right_click(random.randint(973, 1015), 10)
        elif '坐骑酒肆' == self.auto_fight_setting['character_restore_type']:
            inputautogui.press(self.auto_fight_setting['stay'])
            click_button("confirm_rest_button")

    def restore_character_mp_command(self):
        if '右键状态条' == self.auto_fight_setting['character_restore_type']:
            self.click_dialog()
            game_mouse.move_right_click(random.randint(973, 1015), 21)
        elif '坐骑酒肆' == self.auto_fight_setting['character_restore_type']:
            inputautogui.press(self.auto_fight_setting['stay'])
            click_button("confirm_rest_button")

    def restore_bb_hp_command(self):
        if '右键状态条' == self.auto_fight_setting['bb_restore_type']:
            self.click_dialog()
            game_mouse.move_right_click(random.randint(852, 895), 10)
        elif '坐骑巫医' == self.auto_fight_setting['bb_restore_type']:
            inputautogui.press(self.auto_fight_setting['wuyi'])
            click_button("confirm_rest_button")

    def restore_bb_mp_command(self):
        if '右键状态条' == self.auto_fight_setting['bb_restore_type']:
            self.click_dialog()
            game_mouse.move_right_click(random.randint(852, 895), 21)
        elif '坐骑巫医' == self.auto_fight_setting['bb_restore_type']:
            inputautogui.press(self.auto_fight_setting['wuyi'])
            click_button("confirm_rest_button")

    def __refresh_auto_fight_times(self):
        """
        重置自动战斗次数
        :return:
        """
        # 获取当前时间的秒数部分
        current_second = datetime.now().second
        if current_second == 50:
            residue_times = int(self.detect_residue_fight_times())
            randint_one = random.randint(0, 10)
            if randint_one < 9:
                randint = random.randint(6, 22)
            else:
                randint = random.randint(22, 30)
            # 如果剩余战斗次数小于此次随机数则要重置自动战斗次数
            if residue_times < randint:
                # 找到自动战斗窗口的坐标
                result_resetting = match_img(self.__screenshot(), get_source('auto_fight_resetting_button'), 10, 10,
                                             0.95)
                if result_resetting[3] is not None:
                    if click_button('auto_fight_resetting_button'):
                        print("重置自动战斗,成功!")
                    else:
                        print("重置自动战斗,失败!")

    def detect_residue_fight_times(self):
        """
        通过ocr识别自动战斗剩余次数
        :return:
        """
        # 读取剩余战斗次数前(否则可能会遮挡自动战斗悬浮框)先检查是否有对话框并处理 循环三次(有的对话框可能要点击多次)
        self.click_dialog()

        result = match_img(self.__screenshot(), get_source('auto_fight_title'), 10, 10, 0.90)
        if result[3] is None:
            return
        x_offset, y_offset = result[3]['rectangle'][0]
        corp = crop_image_data(self.__screenshot(), (72 + x_offset, 24 + y_offset), (89 + x_offset, 42 + y_offset))
        result = cn_ocr.ocr(corp)
        if result[0] is None:
            return
        return result[0]['text']

    def click_dialog(self):
        """
        检查当前页面是否有对话框,有的话点掉
        :return:
        """
        while True:
            screen_shot = self.__screenshot()
            result_dialog = match_img(screen_shot, get_source('dialog'), 10, 10, 0.90)
            if result_dialog[3] is not None:
                target_x, target_y = random_button_coordinate(result_dialog[3]['rectangle'])
                game_mouse.move_click(target_x, target_y)
            else:
                break

    def __automation(self, fight_type, rate):
        while not auto_fight_stop_event.is_set():
            # TODO 收集训练集期间需手动处理弹窗
            self.__auto_click_four_people(fight_type, rate)
            self.__auto_action()
            time.sleep(2)
            # self.__handle_click()
            # self.__auto_action()
            # self.__refresh_auto_fight_times()

    def run(self, fight_type=0, rate=0.85):
        self.__automation(fight_type, rate)
        # try:
        #     self.__automation(fight_type, rate)
        # except Exception as e:
        #     # if type(e) == pywintypes.error:
        #     print(e)
        #     logger.error(e)
        #     if e.args[0] == 1400:
        #         logger.info("Game was closed")
        #         return


if __name__ == '__main__':
    AutoFightTask = AutoFight(WINDOW_ID, auto_fight_setting)
    AutoFightTask.run()
