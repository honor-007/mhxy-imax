import random
import time

from script_utils.csvUtil import escort_data
from script_utils.grabScreen import winShot
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img, crop_image_data
from src.components.gameMouse import game_mouse
from src.components.status import isFight
from src.components.InputAutoGui import inputautogui
from src.components.window import WINDOW_ID, NAME
from src.modules.check import click_check
from src.modules.map import MapTask, click_button, click_button_v2
from src.modules.npc import NpcTask
from src.modules.props import PropsFunction
from src.modules.task import get_task_info, escort_npc
from src.utils.globalVariable import escort_stop_event
from assets.sources import *
from src.utils.log_util import log_queue

TaskNpc = "郑镖头"
TaskType = "押镖"
TaskLocation = "长风镖局"


def fly_to(location, retry=3):
    """
    进入镖局内场景
    :param location:
    :return:
    """
    if retry <= 0:
        log_queue.put("多次尝试进入长风镖局场景失败,停止尝试...")
        return False
    log_queue.put("使用飞行旗传送到镖局...")
    now = MapTask.GetMapName()
    if now == location:
        return
    if escort_stop_event.is_set():
        return
    PropsFunction.openProps()
    time.sleep(0.5)
    # 找镖局的飞行旗道具 例如:黄色飞行旗
    res = PropsFunction.findProps(escort_setting['flag_type'])
    if not res:
        return fly_to(location)
    if escort_stop_event.is_set():
        return
    game_mouse.move(res[0], res[1], bias=5)
    game_mouse.right_click()
    time.sleep(random.randint(5, 10) / 10)
    screenshot = winShot(WINDOW_ID)
    # result = match_img(screenshot, get_source('b_j_flag'), 10, 10, 0.95)
    if '合成旗' in escort_setting['flag_type']:
        # result = match_img(screenshot, get_source('b_j_flag'), 10, 10, 0.95)
        result = match_img(screenshot, get_source('map_changan'), 10, 10, 0.90)
        if result[3] is None:
            log_queue.put("未匹配到长安城地图")
            return
        x_compensation = result[3]['rectangle'][0][0]
        y_compensation = result[3]['rectangle'][0][1]
        # 截取镖局附近的图
        img_crop_biaoju = crop_image_data(screenshot, left_up=(x_compensation + 500, y_compensation + 100),
                                          right_down=(x_compensation + 550, y_compensation + 160))
        result = match_img(img_crop_biaoju, get_source('map_red_point'), 10, 10, 0.95)
        if result[3] is None:
            log_queue.put("未匹配到镖局传送点的红色点位")
            return
        x = x_compensation + 500 + result[3]['result'][0]
        y = y_compensation + 100 + result[3]['result'][1]

        if escort_stop_event.is_set():
            return
        game_mouse.move_click(x, y, bias=3)
    else:
        # 使用导标旗传送
        # TODO move下图片还没有
        click_result_2 = click_button_v2('single_flag_yes_i_will_go')

    PropsFunction.closeProps()
    time.sleep(random.randint(5, 10) / 10)
    if MapTask.GetMapName() != "长安城":
        return fly_to(location)
    # 进入镖局房屋内
    log_queue.put("进入镖局房屋内...")
    inputautogui.hotkey('alt', 'h')
    inputautogui.press('f9')
    game_mouse.move_click(582 + random.randint(1, 5) * random.choice([-1, 1]),
                          360 + random.randint(1, 5) * random.choice([-1, 1]), bias=5)
    time.sleep(1)
    if MapTask.GetMapName() != "长风镖局":
        return fly_to(location, retry=retry - 1)

    # time.sleep(random.randint(5, 10) / 10)
    # 向郑镖头移动
    log_queue.put("进入长风镖局后第一次向郑镖头移动...")
    game_mouse.move_click(random.randint(800, 950), random.randint(350, 400), bias=20)
    # game_mouse.move_click(612 + random.randint(1, 50) * random.choice([1]),
    #                       253 + random.randint(1, 20) * random.choice([-1, 1]), bias=20)
    time.sleep(random.randint(20, 25) / 10)
    return True


def get_escort_task(level=4):
    """
    接取押镖任务
    :param level:押镖任务等级
    :return:是否成功
    """
    log_queue.put("开始领取押镖任务...")
    task_info = get_task_info(TaskType)
    if task_info:
        log_queue.put(f"当前已有押镖任务,任务目的地:{task_info}...")
        return 0
    if escort_stop_event.is_set():
        return 1
    fly_to(TaskLocation)
    if escort_stop_event.is_set():
        return 1
    # 去郑镖头附近
    NpcTask.go_npc(TaskNpc)
    log_queue.put(f"达到郑镖头附近")
    # 识别郑镖头坐标
    result = NpcTask.findNpc(TaskNpc)
    if not result:
        return
    log_queue.put(f"成功识别郑镖头,坐标x:{result[0]},y:{result[1]},点击郑镖头领取任务")
    game_mouse.move_click(result[0], result[1])
    time.sleep(round(random.random() * 2, 1))

    # click task button
    check_result = click_check(retry=5, sleep_time=30)

    # 遇到弹窗则要重新点击npc
    if check_result:
        log_queue.put(f"检测弹窗处理完成")
        result = NpcTask.findNpc(TaskNpc)
        if not result:
            return
        game_mouse.move_click(result[0], result[1])
        time.sleep(3)
    # 选择任务
    log_queue.put(f"选择领取{level}级镖银任务")
    inputautogui.move_rel(random.randint(0, 20), random.randint(10, 50))
    if not click_button(f"escort_{level}"):
        log_queue.put(f"领取{level}级镖银任务失败")
        return 1
    log_queue.put(f"领取{level}级镖银任务成功")
    inputautogui.move_rel(random.randint(0, 20), random.randint(10, 50))
    time.sleep(random.randint(5, 10) / 10)
    if "储备金" == escort_setting['reward_type']:
        if not click_button("reserves"):
            if not click_button('reserves_two'):
                log_queue.put(f"领取{level}级镖银任务失败")
                return 1
    else:
        if not click_button("cash"):
            if not click_button('cash_two'):
                log_queue.put(f"领取{level}级镖银任务失败")
                return 1
    time.sleep(random.randint(5, 10) / 10)
    game_mouse.left_click()
    return 0


def finish_escort_task(npc):
    """
    完成任务
    :param npc:押镖目的地的npc名称
    :return:
    """
    if escort_stop_event.is_set():
        return

    # 获取目的npc的地图场景名称,比如三大王的location是'老雕洞'
    loc = npc_data[npc]["location"]
    MapTask.MoveToTarget(loc, "None")

    while True:
        # 停止节点
        if escort_stop_event.is_set():
            return

        while isFight.is_fighting():
            if escort_stop_event.is_set():
                return
            time.sleep(random.randint(500, 1000) / 1000)
        # 判断是否有押镖任务 没有就退出
        task_info = get_task_info(TaskType)
        if not task_info:
            return

        NpcTask.go_npc(npc)
        result = NpcTask.findNpc(npc)
        if not result:
            continue
        # 停止节点
        if escort_stop_event.is_set():
            return
        game_mouse.move(result[0], result[1])
        inputautogui.hotkey("alt", "g")
        time.sleep(0.1)
        inputautogui.left_click()
        time.sleep(random.randint(5, 10) / 10)
        if not PropsFunction.isPropsToNpc():
            # 停止节点
            if escort_stop_event.is_set():
                return
            inputautogui.right_click()
            time.sleep(0.1)
            continue
        result = PropsFunction.findProps(f"镖银包裹_{escort_setting['escort_level']}")
        if not result:
            continue
        # 停止节点
        if escort_stop_event.is_set():
            return
        game_mouse.move_click(result[0], result[1])
        time.sleep(0.1)

        # press give button
        result = click_button("confirm_give")
        if not result:
            continue
        time.sleep(3)
        # 停止节点
        if escort_stop_event.is_set():
            return
        inputautogui.left_click()
    escort_data.add_task_time(NAME)


def escort_one_time():
    # 领取押镖任务
    while get_escort_task(escort_setting['escort_level']) != 0:
        if escort_stop_event.is_set():
            return
        continue

    # 获取任务目的npc
    npc = escort_npc()

    log_queue.put(f"当前已有押镖任务,需将镖银送到:{npc}...")
    if escort_stop_event.is_set():
        return

    # 完成押镖任务
    finish_escort_task(npc)
