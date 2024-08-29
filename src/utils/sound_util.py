import time

import pygame

from assets.sources import get_source
from src.utils.globalVariable import alarm_stop_event
from src.utils.log_util import log_queue


def playsound():
    pygame.init()
    # 加载音频文件
    # 注意：确保音频文件的路径是正确的
    sound = pygame.mixer.Sound(get_source('alarm_sound'))
    # 播放音频
    while not alarm_stop_event.is_set():
        sound.play()
        time.sleep(1.6)
    alarm_stop_event.clear()
    # 等待音频播放完毕
    while pygame.mixer.get_busy():
        pygame.time.wait(100)
    # 退出 pygame
    pygame.quit()
    for i in range(5):
        log_queue.put(f"脚本将在{5 - i}s后继续运行,请保持梦幻西游窗口在当前页面")
        time.sleep(1)


if __name__ == "__main__":
    playsound()
