from src.utils.globalVariable import *
from src.utils.log_util import log_queue
from src.windows.applicationWindow import AppilcationGui

application = AppilcationGui()


def on_close_application_window():
    stop_event_all_set()
    log_queue.put("任务关闭...")
    application.destroy()


def start_application_window():
    application.protocol("WM_DELETE_WINDOW", on_close_application_window)
    # 启动线程
    t = threading.Thread(target=application.log_info, args=())
    t.start()
    log_queue.put("任务未启动...")
    application.mainloop()


if __name__ == "__main__":
    print("!")
    start_application_window()
