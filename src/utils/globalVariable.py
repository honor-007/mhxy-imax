import threading

from src.utils.log_util import log_stop_event

task_stop_event = threading.Event()

escort_stop_event = threading.Event()

alarm_stop_event = threading.Event()

auto_fight_stop_event = threading.Event()

dazuo_stop_event = threading.Event()

mouse_stop_event = threading.Event()

# 任务线程标志
module_task_stop_event = threading.Event()

hover_image_save_path = r'E:\temp\hover'
check_image_save_path = r'E:\temp\check'


def stop_event_all_set():
    log_stop_event.set()
    escort_stop_event.set()
    alarm_stop_event.set()
    auto_fight_stop_event.set()
    dazuo_stop_event.set()
    mouse_stop_event.set()


def stop_escort_event():
    stop_auto_fight_event()
    escort_stop_event.set()

def clear_escort_event():
    clear_auto_fight_event()
    escort_stop_event.clear()

def stop_auto_fight_event():
    alarm_stop_event.set()
    auto_fight_stop_event.set()
    dazuo_stop_event.set()
    mouse_stop_event.set()
    module_task_stop_event.set()


def clear_auto_fight_event():
    alarm_stop_event.clear()
    auto_fight_stop_event.clear()
    dazuo_stop_event.clear()
    mouse_stop_event.clear()
    module_task_stop_event.clear()
