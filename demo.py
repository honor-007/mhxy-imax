import os
import time

import cv2

from assets.sources import props_data, get_source, location_data, location_name_supplement_data
from script_utils.cnOcr import cn_ocr, get_chinese_text, get_closed_string
from script_utils.imageTransform import hsvFilterLocationWhite
from script_utils.matchTemplate import match_img, crop_image_data
from src.modules.props import PropsFunction


# time.sleep(2)
# res = PropsFunction.findProps('白色导标旗')

# basedir = os.path.abspath(os.path.dirname(__file__))
# template = os.path.join(basedir, 'assets\\props', props_data['白色导标旗'])
# result = match_img('test.png', template, 10, 10, 0.95)
# if result[3] is None:
#     print("none")
# else:
#     print(result[3]['result'])


# result = match_img('test2.png', get_source('single_flag_dialog'), 10, 10, 0.90)
# if result[3] is None:
#     print("none")
# else:
#     print(result[3]['result'])


def GetMapName(self) -> str:
    screenshot = cv2.imread('test3.png')
    img = crop_image_data(screenshot, left_up=(18, 24),
                          right_down=(140, 42))

    cv2.imshow("22",img)
    raw_text = cn_ocr.ocr_for_single_line(hsvFilterLocationWhite(img, mask=True))['text']
    chinese_text = get_chinese_text(raw_text)
    location_name_list = [location for location in location_data.keys()] + [location for location in
                                                                            location_name_supplement_data]
    return get_closed_string(chinese_text, location_name_list)


name = GetMapName()
print(name)