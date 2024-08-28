import cv2

from script_utils.loggerConfig import logger
import game_models.hoverModel as hm
from assets.sources import get_source
from config import hover_list
from script_utils.cnOcr import cn_ocr
from script_utils.imageTransform import hsvFilterWordWhite, mutil_crop, hsvFilterFourPeopleWhite
from script_utils.matchTemplate import match_img, crop_image_data
from src.utils.img_util import save_fight_normal_check, save_fight_reward_check


def rewardNotification(rate=0.9):
    # 1. 截取mhxy的窗口截图
    screenshot = cv2.imread("test2.png")
    # 2. 处理截图并识别文字
    outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
    # 3. 截图和hover_reward.png做匹配
    result = match_img(screenshot, get_source['hover_reward'], 10, 10, rate)
    # 4
    if result[3] is not None:
        x, y = result[3]['rectangle'][3]
        # 分割(请点击朝向你的人物)图像
        mutil_crop(screenshot, hover_list, (x - 350, y + 15), (x + 10, y + 155))
        # TODO 收集训练集用 正式环境删除
        save_fight_reward_check(screenshot)
        return True
    # 5. 若List outs不为空
    if outs:
        for out in outs:
            text = out['text']
            # 获取 检测出的文字对应的矩形框 的左上坐标
            xs, ys = out['position'][3]
            xs, ys = int(xs), int(ys)
            if ys > 600 or xs < 200 or xs > 850:
                continue
            if '恭' or "喜" in text:
                x, y = out['position'][3]
                x, y = int(x), int(y)
                mutil_crop(screenshot, hover_list, (x, y), (x + 360, y + 140))
                # TODO 收集训练集用 正式环境删除
                save_fight_reward_check(screenshot)
                return True
    return False


def normalNotification(rate=0.9):
    """
    识别是否存在普通弹窗
    :param rate:
    :return:
    """
    screenshot = cv2.imread("test2.png")
    outs = cn_ocr.ocr(hsvFilterFourPeopleWhite(screenshot))
    result = match_img(screenshot, get_source('hover_normal'), 10, 10, rate)
    if result[3] is not None:
        x, y = result[3]['rectangle'][3]
        # crop_img = crop_image_data(screenshot, left_up=(x - 230, y + 2),
        #                            right_down=(x + 120, y + 142))
        # cv2.imshow("22", crop_img)
        # cv2.waitKey()

        # mutil_crop(screenshot, hover_list, (x - 350, y + 15), (x + 10, y + 155))
        mutil_crop(screenshot, hover_list, (x - 230, y + 2), (x + 120, y + 142))
        # TODO 收集训练集用 正式环境删除
        save_fight_normal_check(screenshot)
        return True
    if outs:
        for out in outs:
            text = out['text']
            xs, ys = out['position'][3]
            xs, ys = int(xs), int(ys)
            if ys > 600 or xs < 200 or xs > 850:
                continue
            if "请选择" in text:
                x, y = out['position'][3]
                x, y = int(x), int(y)
                mutil_crop(screenshot, hover_list, (x, y), (x + 360, y + 140))
                # TODO 收集训练集用 正式环境删除
                save_fight_normal_check(screenshot)
                return True
    return False


def __task(fight_type=0, rate=0.85):
    if fight_type == 0:
        if normalNotification(rate):
            logger.info("存在弹窗：切割完毕")
            return True
    elif fight_type == 1:
        if rewardNotification(rate):
            logger.info("存在奖励弹窗：切割完毕")
            return True
    return False


fight_type = 0
rate = 0.85

if __task(fight_type, rate):
    min_index = hm.model_predict(hover_list)
