from tkinter.messagebox import *


class ExceptionGui():
    """
    激活窗口
    """

    def __init__(self, title, message):
        self.title = title
        self.message = message

    def init_window(self):
        showinfo(title=self.title, message=self.message)


if __name__ == "__main__":
    exceptionGui = ExceptionGui('错误', '警告测试')
    exceptionGui.init_window()
    # exceptionGui.start_activate_window()
