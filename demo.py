import threading
import time

from src.utils.log_util import log_queue


def dazuo(var=1):
    print(f"kaishi dazuo:{var}")
    time.sleep(5)
    print(f"jieshu dazuo:{var}")


log_queue.put("启动打坐线程")
# dazuo_thread = threading.Thread(target=stay(1))
# dazuo2_thread = threading.Thread(target=stay(2))

escort_thread = threading.Thread(target=dazuo, args=("1"))
auto_fight_thread = threading.Thread(target=dazuo, args=('2'))
escort_thread.start()
auto_fight_thread.start()

print("zhixingwanbi")
time.sleep(10)
print("over")
