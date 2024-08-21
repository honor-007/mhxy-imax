import os
import threading
import time

import cv2

from assets.sources import get_source, location_data
from script_utils.cnOcr import cn_ocr, get_chinese_text, get_closed_string
from script_utils.imageTransform import hsvFilterLocationWhite
from script_utils.matchTemplate import match_img, crop_image_data
level=3
result = match_img("test8.png", get_source(f"escort_{level}"), 10, 10, 0.95)[3]
print(result)