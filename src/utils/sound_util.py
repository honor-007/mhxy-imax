import pygame


def playsound(path='../../assets/sound/alarm.mp3'):
    pygame.init()
    # 加载音频文件
    # 注意：确保音频文件的路径是正确的
    sound = pygame.mixer.Sound(path)
    # 播放音频
    sound.play()
    # 等待音频播放完毕
    while pygame.mixer.get_busy():
        # pygame.time.Clock().tick(10)
        pygame.time.wait(100)
    # 退出 pygame
    pygame.quit()
