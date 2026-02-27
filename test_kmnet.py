import time
import kmNet
import pyautogui


def main():
    # 初始化 kmbox 连接
    result = kmNet.init('192.168.2.188', '4552', 'DDE80C3D')
    if result != 0:
        print('kmbox 连接失败')
        return
    print('kmbox 连接成功，3秒后开始执行...')

    time.sleep(3)
    # kmNet.enc_left(1)

    # ========== 测试0: move_auto ==========
    print('\n========== 测试0: move_auto ==========')
    start_pos = pyautogui.position()
    print(f'起始位置: {start_pos}')

    kmNet.enc_move_auto(50, -148,2000)
    time.sleep(0.3)

    end_pos = pyautogui.position()
    print(f'结束位置: {end_pos}')
    print(f'实际移动距离: x={end_pos[0] - start_pos[0]}, y={end_pos[1] - start_pos[1]}')


    # # ========== 测试1: enc_move_auto ==========
    # print('\n========== 测试1: enc_move_auto ==========')
    # start_pos = pyautogui.position()
    # print(f'起始位置: {start_pos}')
    #
    # kmNet.enc_move_auto(300, 0,200)
    # time.sleep(0.3)
    #
    # end_pos = pyautogui.position()
    # print(f'结束位置: {end_pos}')
    # print(f'实际移动距离: x={end_pos[0] - start_pos[0]}, y={end_pos[1] - start_pos[1]}')
    #
    #
    # # ========== 测试2: enc_move_beizer（控制点在直线上） ==========
    # print('\n========== 测试2: enc_move_beizer（控制点在直线上） ==========')
    # start_pos = pyautogui.position()
    # print(f'起始位置: {start_pos}')
    #
    # # 控制点在直线上：(33, 0), (66, 0)
    # kmNet.enc_move_beizer(1000, 0, 200, 33, 0, 66, 0)
    # time.sleep(0.3)
    #
    # end_pos = pyautogui.position()
    # print(f'结束位置: {end_pos}')
    # print(f'实际移动距离: x={end_pos[0] - start_pos[0]}, y={end_pos[1] - start_pos[1]}')


    # # ========== 测试3: enc_move_beizer（控制点偏离直线） ==========
    # print('\n========== 测试3: enc_move_beizer（控制点偏离直线） ==========')
    # start_pos = pyautogui.position()
    # print(f'起始位置: {start_pos}')
    #
    # # 控制点偏离直线：(33, 6), (66, -6)
    # # kmNet.enc_move_beizer(1, 0, 200, 33, 6, 66, -6)
    # # time.sleep(0.3)
    #
    # end_pos = pyautogui.position()
    # print(f'结束位置: {end_pos}')
    # print(f'实际移动距离: x={end_pos[0] - start_pos[0]}, y={end_pos[1] - start_pos[1]}')

    # kmNet.enc_left(0)

    print('\n执行完成')


if __name__ == '__main__':
    main()
