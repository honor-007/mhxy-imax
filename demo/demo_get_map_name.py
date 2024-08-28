import cv2

from assets.sources import location_data, location_name_supplement_data
from script_utils.cnOcr import cn_ocr, get_chinese_text, get_closed_string
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterLocationWhite
from script_utils.matchTemplate import crop_image_data
from src.components.window import WINDOW_ID


def __screenshot():
    print(f"WINDOW_ID:{WINDOW_ID}")
    return winShot(WINDOW_ID)


def GetMapName() -> str:
    screenshot = cv2.imread('lingtaigong.png')
    img = crop_image_data(screenshot, left_up=(18, 24),
                          right_down=(140, 42))
    raw_text = cn_ocr.ocr_for_single_line(hsvFilterLocationWhite(img, mask=True))['text']
    chinese_text = get_chinese_text(raw_text)
    location_name_list = [location for location in location_data.keys()] + [location for location in
                                                                            location_name_supplement_data]

    return get_closed_string(chinese_text, location_name_list)


map_name = GetMapName()
print(map_name)
