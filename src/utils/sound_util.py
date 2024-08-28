import time

import pygame

from src.utils.globalVariable import alarm_stop_event


def playsound(path='../../assets/sound/alarm.mp3'):
    pygame.init()
    # 加载音频文件
    # 注意：确保音频文件的路径是正确的
    sound = pygame.mixer.Sound(path)
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

if __name__ == "__main__":
    playsound()