# -*- coding: gbk -*-
import random
import time

import win32gui

import game_models.hoverModel as hm
from assets.sources import get_source, auto_fight_setting
from config import hover_list
from script_utils.grabScreen import winShot
from script_utils.imageTransform import get_hp_rect, get_mp_rect
from script_utils.matchTemplate import match_img, crop_image_data
from src.components.InputAutoGui import inputautogui
from src.components.gameMouse import game_mouse
from src.components.hover import hover
from src.components.status import isFight
from src.components.window import WINDOW_ID
from src.modules.map import click_button
from src.utils import sound_util
from src.utils.globalVariable import auto_fight_stop_event, module_task_stop_event, log_queue
from src.utils.img_util import save_fight_normal_check
from src.utils.other_util import if_windows_in_screen
from src.utils.random_util import random_button_coordinate


class AutoFight:
    def __init__(self, hwnd, auto_fight_setting):
        self.hwnd = hwnd
        self.name = win32gui.GetWindowText(hwnd)
        self.auto_fight_setting = auto_fight_setting
        self.is_fighting = True

    def __screenshot(self):
        return winShot(self.hwnd)

    def __if_have_notification_check(self, rate=0.95):
        # if not self.__windows_in_screen():
        #     log_queue("梦幻西游不在当前窗口,无法进行游戏鼠标移动...")
        #     return False
        self.__if_windows_in_screen()
        if hover.normalNotification(rate):
            log_queue.put("检测到普通弹窗")
            return True
        elif hover.rewardNotification(rate):
            log_queue.put("检测到奖励弹窗1")
            return True
        # elif hover.rewardMaskNotification(rate):
        #     log_queue.put("检测到奖励弹窗2")
        #     return True
        else:
            return False

    # def __windows_in_screen(self):
    #     """
    #     判断当前窗口是否是mhxy的窗口
    #     :return:
    #     """
    #     return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name

    def __if_windows_in_screen(self):
        """
        判断当前窗口是否是mhxy的窗口
        :return:
        """
        if module_task_stop_event.is_set():
            module_task_stop_event.clear()
            return
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.name:
            return
        else:
            log_queue("梦幻西游不在当前窗口,请将梦幻西游窗口打开为当前窗口...")
            time.sleep(1)
            self.__if_windows_in_screen()
            return

    def __auto_click_four_people(self, rate=0.85):
        # 有弹窗并完成切割返回true 否则false
        if not self.__if_have_notification_check(rate):
            return
        min_index = hm.model_predict(hover_list)
        # TODO 计算点击坐标(暂时设置为 识别出的切割图片的中心位置)
        screen_shot = self.__screenshot()
        result = match_img(screen_shot, hover_list[min_index], 10, 10, 0.95)
        if result[3] is None:
            log_queue.put("匹配失败弹窗点击失败,需要手动处理")
            save_fight_normal_check(screen_shot)
            sound_util.playsound()
            return
        target_x, target_y = result[3]['result']

        if target_x == 0 and target_y == 0:
            log_queue.put("匹配失败弹窗点击失败,需要手动处理")
            save_fight_normal_check(screen_shot)
            sound_util.playsound()
        else:
            log_queue.put(f'根据预测结果,点击坐标为[x：{target_x} < ; y：{target_y}]')
            game_mouse.move_click(target_x, target_y)
            time.sleep(0.5)
            if self.__if_have_notification_check(rate):
                log_queue.put("匹配失败弹窗点击失败,需要手动处理")
                # TODO 收集预测失败的图片
                save_fight_normal_check(screen_shot)
                sound_util.playsound()

    def __auto_fight_first_step(self, rate=0.85):
        """
        :param fight_type:
        :param rate:
        :return:
        """
        if isFight.is_fighting():
            self.is_fighting = True
            log_queue.put("战斗中,检查并处理弹窗")
            self.__auto_click_four_people(rate=0.85)
        else:
            # 非战斗中的处理
            # 恢复
            if self.is_fighting:
                self.is_fighting = False
                log_queue.put("战斗结束,检查任务状态...")
                self.restore()
                if '无' != self.auto_fight_setting['dazuo']:
                    time.sleep(random.randint(1, 3))
                    if not isFight.is_fighting():
                        log_queue.put("打坐回蓝...")
                        inputautogui.press(self.auto_fight_setting['dazuo'])

    def __auto_action(self):
        """
        攻击操作
        :return:
        """
        if isFight.is_fighting():
            log_queue.put("战斗中,弹窗已处理完毕,执行战斗操作")
            if isFight.is_need_fight_action():
                if self.auto_fight_setting["character_attack"] == "alt+a":
                    inputautogui.hotkey('alt', 'a')
                elif self.auto_fight_setting["character_attack"] == "alt+q":
                    inputautogui.hotkey('alt', 'q')
                elif self.auto_fight_setting["character_attack"] == "alt+d":
                    inputautogui.hotkey('alt', 'd')
                time.sleep(random.randint(0, 5) / 10)
                if self.auto_fight_setting["bb_attack"] == "alt+a":
                    inputautogui.hotkey('alt', 'a')
                elif self.auto_fight_setting["bb_attack"] == "alt+q":
                    inputautogui.hotkey('alt', 'q')
                elif self.auto_fight_setting["bb_attack"] == "alt+d":
                    inputautogui.hotkey('alt', 'd')
                # 操作完再检查一次以提高程序健壮性
                if isFight.is_need_fight_action():
                    # 如何战斗操作栏还在,说明没操作成功
                    # 1.检查鼠标形状是否变成了施法形状(如果两场战斗相隔时间太近,又开启了酒肆/巫医恢复的话,可能会在战斗中按下酒肆/巫医快捷键)
                    result = match_img(self.__screenshot(), get_source("disable_mouse"), 10, 10, 0.95)[3]
                    if result is not None:
                        inputautogui.right_click()
                        return self.__auto_action()
                    # result = match_img(self.__screenshot(), get_source("magic_mouse"), 10, 10, 0.95)[3]
                    # if result is not None:
                    #     inputautogui.right_click()
                    #     return self.__auto_action()
                    # 2.如果不是1的影响,可能是alt没生效只按了q,导致在打字
            return True
        return False

    def restore(self):
        # log_queue.put("检查人物和bb状态是否需要恢复")
        img = self.__screenshot()
        state_width = 50
        # 截取人物状态栏
        character_img = crop_image_data(img, (955, 5), (1020, 50))

        # x, y, w, h = get_hp_rect(character_img)
        result = get_hp_rect(character_img)
        if result is not None and result[2] > 0:
            log_queue.put("人物hp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            character_hp_rate = round(result[2] / state_width * 100)
            log_queue.put(" character_hp_rate:{}".format(character_hp_rate))
            if character_hp_rate <= int(self.auto_fight_setting["character_hp_threshold"][:-1]):
                log_queue.put(
                    f'人物气血百分比{character_hp_rate},小于{self.auto_fight_setting["character_hp_threshold"]},需要执行加血指令')
                self.restore_character_hp_command()
        else:
            log_queue.put("未读取到人物hp,不做操作")

        # x, y, w, h = get_mp_rect(character_img)
        result = get_mp_rect(character_img)
        if result is not None and result[2] > 0:
            log_queue.put("人物mp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            character_mp_rate = round(result[2] / state_width * 100)
            log_queue.put(" character_mp_rate:{}".format(character_mp_rate))
            if character_mp_rate <= int(self.auto_fight_setting["character_mp_threshold"][:-1]):
                log_queue.put(
                    f'人物魔法百分比:{character_mp_rate},小于{self.auto_fight_setting["character_mp_threshold"]},需要执行加蓝指令')
                self.restore_character_mp_command()
        else:
            log_queue.put("未读取到人物mp,不做操作")

        bb_img = crop_image_data(img, (845, 5), (900, 38))
        result = get_hp_rect(bb_img)
        if result is not None and result[2] > 0:
            log_queue.put("宠物hp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            bb_hp_rate = round(result[2] / state_width * 100)
            if bb_hp_rate <= int(self.auto_fight_setting["bb_hp_threshold"][:-1]):
                log_queue.put(
                    f'bb气血百分比:{bb_hp_rate},小于{self.auto_fight_setting["bb_hp_threshold"]},需要执行加血指令')

                self.restore_bb_hp_command()
        else:
            log_queue.put("未读取到宠物hp,不做操作")

        # x, y, w, h = get_mp_rect(bb_img)
        result = get_mp_rect(bb_img)
        if result is not None and result[2] > 0:
            log_queue.put("宠物mp x:{}, y:{}, w:{}, h:{}".format(result[0], result[1], result[2], result[3]))
            bb_mp_rate = round(result[2] / state_width * 100)
            if bb_mp_rate <= int(self.auto_fight_setting["bb_mp_threshold"][:-1]):
                log_queue.put(
                    f'bb魔法百分比:{bb_mp_rate},小于{self.auto_fight_setting["bb_mp_threshold"]},需要执行加蓝指令')
                self.restore_bb_mp_command()
        else:
            log_queue.put("未读取到宠物mp,不做操作")

    def restore_character_hp_command(self):
        if '右键状态条' == self.auto_fight_setting['character_restore_type']:
            # 如果是右键恢复前先检查是否有对话框并处理
            self.click_dialog()
            game_mouse.move_right_click(random.randint(973, 1015), 10)
        elif '坐骑酒肆' == self.auto_fight_setting['character_restore_type']:
            game_mouse.locked_client_move(random.randint(500, 700), random.randint(200, 400))
            inputautogui.press(self.auto_fight_setting['stay'])
            time.sleep(random.randint(10, 15) / 10)
            target_x = random.randint(215, 255)
            target_y = random.randint(478, 480)
            game_mouse.move_click(target_x, target_y, bias=3)

    def restore_character_mp_command(self):
        if '右键状态条' == self.auto_fight_setting['character_restore_type']:
            self.click_dialog()
            game_mouse.move_right_click(random.randint(973, 1015), 21)
        elif '坐骑酒肆' == self.auto_fight_setting['character_restore_type']:
            game_mouse.locked_client_move(random.randint(500, 700), random.randint(200, 400))
            inputautogui.press(self.auto_fight_setting['stay'])
            time.sleep(random.randint(10, 15) / 10)
            target_x = random.randint(215, 255)
            target_y = random.randint(478, 480)
            game_mouse.move_click(target_x, target_y, bias=3)

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

    def click_dialog(self):
        """
        检查当前页面是否有对话框,有的话点掉
        :return:
        """
        while True:
            screen_shot = self.__screenshot()
            result_dialog = match_img(screen_shot, get_source('dialog'), 10, 10, 0.90)
            if result_dialog[3] is not None:
                target_x, target_y, padding = random_button_coordinate(result_dialog[3]['rectangle'])
                game_mouse.move_click(x=target_x, y=target_y, bias=padding)
            else:
                break

    def __automation(self, fight_type, rate):
        while not auto_fight_stop_event.is_set():
            if_windows_in_screen()
            self.__auto_fight_first_step(rate)
            self.__auto_action()
            time.sleep(0.5)

    def run(self, fight_type=0, rate=0.85):
        self.__automation(fight_type, rate)


if __name__ == '__main__':
    AutoFightTask = AutoFight(WINDOW_ID, auto_fight_setting)
    AutoFightTask.run()
