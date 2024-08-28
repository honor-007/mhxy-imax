import cv2

from assets.sources import npc_data, get_source
from script_utils.cnOcr import get_closed_string, cn_ocr
from script_utils.imageTransform import hsvFilterTaskRed, hsvFilterEscortTaskNpcRed
from script_utils.matchTemplate import match_img, crop_image_data


def get_task_text():
    """
    读取任务内容
    :return:
    """
    screenshot = cv2.imread("sandawang.png")
    result = match_img(screenshot, get_source('task_flag'), 10, 10, 0.95)
    task_text = ""
    if result[3] is None:
        return task_text
    left_up = result[3]['rectangle'][0]
    right_down = result[3]['rectangle'][3]
    crop_data = crop_image_data(screenshot, left_up=(left_up[0] - 136, left_up[1] + 45),
                                right_down=(right_down[0], right_down[1] + 55))
    cv2.imwrite("sandawang_task.png",crop_data)
    cv2.imshow("22", crop_data)
    cv2.waitKey()

    crop_data = hsvFilterEscortTaskNpcRed(crop_data)

    cv2.imshow("22", crop_data)
    cv2.waitKey()

    result = cn_ocr.ocr(crop_data)
    if result:
        for data in result:
            task_text += data['text']
    return task_text


def escort_npc():
    """
    获取押镖目的地npc名称
    :return:
    """
    game_info = get_task_text()
    if game_info == "":
        return ""
    return get_closed_string(game_info, list(npc_data.keys()))


string = escort_npc()
print(string)
