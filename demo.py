import threading

import cv2

from assets.sources import get_source, location_data
from script_utils.cnOcr import cn_ocr, get_chinese_text, get_closed_string
from script_utils.imageTransform import hsvFilterLocationWhite
from script_utils.matchTemplate import match_img, crop_image_data


def GetMapName() -> str:
    screenshot = cv2.imread("guojing.png")
    img = crop_image_data(screenshot, left_up=(18, 24),
                          right_down=(140, 42))

    cv2.imshow("22",img)
    cv2.waitKey()

    raw_text = cn_ocr.ocr_for_single_line(hsvFilterLocationWhite(img, mask=True))['text']
    chinese_text = get_chinese_text(raw_text)
    a = get_closed_string(chinese_text, [location for location in location_data.keys()])
    print(a)
    return a

GetMapName()