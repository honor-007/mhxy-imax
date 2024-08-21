import datetime
import os
import time

import cv2


def save_image(img, type='unknow'):
    basedir = os.path.abspath(os.path.dirname(__file__))

    if type == 'is_have_check':
        folder_path = os.path.join(basedir, "is_have_check")
    else:
        folder_path = os.path.join(basedir, "unknow")
    now = datetime.datetime.now()
    formatted_time = now.strftime('%Y-%m-%d_%H:%M:%S') + ".png"
    img_path = os.path.join(folder_path, formatted_time)

    cv2.imwrite(img_path, img)
