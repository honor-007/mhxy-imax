import subprocess
import time

import kmNet
import win32gui
from ttkbootstrap.dialogs.dialogs import Messagebox

import config
from assets.sources import system_setting
from src.components.window import WINDOW_ID, get_mhxy_hwnd
from src.utils.globalVariable import log_queue, module_task_stop_event


def check_ping(ip_address):
    # 使用ping命令检查IP是否可达
    command = ['ping', '-n', '1', ip_address]  # 在Linux/MacOS上使用'-c'参数，在Windows上使用'-n'参数
    try:
        # 执行ping命令
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 如果ping成功，则返回True
        return True
    except subprocess.CalledProcessError:
        # 如果ping失败，则返回False
        return False


def init_kmbox():
    if not check_ping(system_setting['IP']):
        Messagebox.show_warning(title='警告', message='kmbox无法ping通,请在系统设置中修正kmbox相关参数配置')
        return False
    result = kmNet.init(system_setting['IP'], system_setting['Port'], system_setting['UUID'])
    if result == 0:
        log_queue.put("kmbox 初始化成功！")
        return True
    else:
        Messagebox.show_warning(title='警告', message='kmbox无法连接,请在系统设置中修正kmbox相关参数配置')
        return False


def before_start_task_check(setting):
    """
    task脚本运行前检查
    :param setting:
    :return:
    """
    # 关键设置检查
    for key, value in setting.items():
        if value is None:
            Messagebox.show_error(title='内容缺失',
                                  message=f'{key}设置内容有缺失,无法启动(不使用坐骑技能请随便设置,不可为空')
            return -1
    # kmbox连接检查
    log_queue.put('开始连接kmbox键鼠...')
    if system_setting['interactor'] == '驱动键鼠':
        if not init_kmbox():
            return -1
    # 当前窗口游戏角色id和激活码绑定角色id匹配(applicationgui打开前已经进行了window_id检查)
    result = get_mhxy_hwnd(use_id=config.main_user)
    if result == -1:
        Messagebox.show_error(title='错误', message='请先确认绑定的角色进入游戏后再执行脚本')

    win32gui.SetForegroundWindow(WINDOW_ID)


def if_windows_in_screen():
    """
    判断当前窗口是否是mhxy的窗口
    :return:
    """
    if module_task_stop_event.is_set():
        # module_task_stop_event.clear()
        return
    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) != win32gui.GetWindowText(WINDOW_ID):
        log_queue.put("梦幻西游不在当前窗口,请将梦幻西游窗口打开为当前窗口...")
        # print('梦幻西游不在当前窗口,请将梦幻西游窗口打开为当前窗口...')
        time.sleep(1)
        if_windows_in_screen()


if __name__ == "__main__":
    if_windows_in_screen()
