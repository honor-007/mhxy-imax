"""
鼠标坐标记录工具 (仅使用 win32api + pyautogui)

功能: 点击鼠标左键时记录当前鼠标的xy坐标
使用: 运行脚本后，点击鼠标左键记录坐标，按ESC键退出

依赖: pyautogui, win32api (项目已有)
"""
import time
import pyautogui
import win32api
import win32con


class MousePositionRecorder:
    """鼠标坐标记录器"""

    def __init__(self):
        self.positions = []
        self.running = True
        self.last_click_time = 0
        self.click_debounce = 0.2  # 防抖时间(秒)

    def is_left_button_pressed(self):
        """检测鼠标左键是否按下"""
        return win32api.GetKeyState(win32con.VK_LBUTTON) < 0

    def is_esc_pressed(self):
        """检测ESC键是否按下"""
        return win32api.GetKeyState(win32con.VK_ESCAPE) < 0

    def start(self):
        """启动记录器"""
        print('='*60)
        print('鼠标坐标记录工具')
        print('='*60)
        print('使用说明:')
        print('  - 点击鼠标左键: 记录当前坐标')
        print('  - 按ESC键: 退出程序')
        print('  - 按Ctrl+C: 强制退出')
        print('='*60)
        print('\n开始监听鼠标点击...\n')

        last_button_state = False
        last_esc_state = False

        try:
            while self.running:
                # 检测ESC键
                current_esc_state = self.is_esc_pressed()
                if current_esc_state and not last_esc_state:
                    print('\n检测到ESC键，准备退出...')
                    break
                last_esc_state = current_esc_state

                # 检测鼠标左键点击
                current_button_state = self.is_left_button_pressed()

                # 检测从未按下到按下的状态变化（点击事件）
                if current_button_state and not last_button_state:
                    current_time = time.time()
                    # 防抖处理
                    if current_time - self.last_click_time > self.click_debounce:
                        x, y = pyautogui.position()
                        self.positions.append((x, y))
                        print(f'[{len(self.positions)}] 记录坐标: x={x}, y={y}')
                        self.last_click_time = current_time

                last_button_state = current_button_state
                time.sleep(0.01)  # 10ms轮询间隔

        except KeyboardInterrupt:
            print('\n检测到Ctrl+C，准备退出...')

        # 输出汇总
        self.print_summary()

    def print_summary(self):
        """打印记录汇总"""
        print('\n' + '='*60)
        print('记录汇总')
        print('='*60)

        if not self.positions:
            print('未记录任何坐标')
        else:
            print(f'共记录 {len(self.positions)} 个坐标:\n')
            for i, (x, y) in enumerate(self.positions, 1):
                print(f'  [{i}] x={x}, y={y}')

            # 输出Python列表格式
            print('\nPython列表格式:')
            print(f'positions = {self.positions}')

            # 输出为元组列表
            print('\n元组列表格式:')
            print('positions = [')
            for x, y in self.positions:
                print(f'    ({x}, {y}),')
            print(']')

            # 输出为字典格式（带索引）
            print('\n字典格式:')
            print('positions = {')
            for i, (x, y) in enumerate(self.positions, 1):
                print(f'    {i}: ({x}, {y}),')
            print('}')

        print('='*60)


def main():
    """主函数"""
    recorder = MousePositionRecorder()
    recorder.start()


if __name__ == '__main__':
    main()
