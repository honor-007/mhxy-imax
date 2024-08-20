import threading
import time
from queue import Queue

log_stop_event = threading.Event()

log_queue = Queue(maxsize=10)


