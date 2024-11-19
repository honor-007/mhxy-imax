from ttkbootstrap.dialogs import Messagebox
from src.utils.globalVariable import log_queue
import src.utils.globalVariable as gv
from assets.sources import activate_setting, system_setting
from src.utils.other_util import init_kmbox


def before_start_check(settings):
    """
    脚本(捉鬼/自动战斗/跑镖...)开始前的统一检查
    """
    if not gv.activate_flag:
        character_id = activate_setting['character_id']
        Messagebox.show_error(title='未激活', message=f'角色[{character_id}]未激活或已到期,请先激活')
        return False
    log_queue.put("开始执行任务...")
    for key, value in settings.items():
        if value is None or value == "":
            Messagebox.show_error(title='内容缺失', message=f'{key}设置内容有缺失,无法启动(不使用坐骑技能请随便设置,不可为空')
            return False
    log_queue.put('开始连接kmbox键鼠...')
    if system_setting['interactor'] == '驱动键鼠':
        if not init_kmbox():
            return False
