import os
import time

import cv2

from src.utils.img_util import save_escort_task_check

img = cv2.imread('test16.png')
save_escort_task_check(img)

