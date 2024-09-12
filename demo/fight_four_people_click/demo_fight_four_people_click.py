import cv2

import game_models.hoverModel as hm
from assets.sources import get_source
from config import hover_list
from script_utils.cnOcr import cn_ocr
from script_utils.imageTransform import hsvFilterWordWhite, mutil_crop, hsvFilterFourPeopleWhite
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img
from src.utils import sound_util
from src.utils.img_util import save_fight_normal_check, save_fight_reward_check

screenshot = cv2.imread(r"2024-09-07_21-38-05.png")
# screenshot = cv2.imread(r"test1.png")

def rewardNotification(rate=0.9):
    """
    奖励弹窗1
    :param rate:
    :return:
    """
    # 2. 处理截图并识别文字
    outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
    # 3. 截图和hover_reward.png做匹配
    result = match_img(screenshot, get_source('hover_reward'), 10, 10, rate)
    # 4
    if result[3] is not None:
        x, y = result[3]['rectangle'][3]
        # 分割(请点击朝向你的人物)图像
        mutil_crop(screenshot, hover_list, (x - 345, y + 12), (x + 5, y + 144))
        # mutil_crop(screenshot, hover_list, (x - 230, y + 2), (x + 120, y + 142))
        # TODO 收集训练集用 正式环境删除
        # save_fight_reward_check(screenshot)
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
            if '恭' in text or "喜" in text:
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
    outs = cn_ocr.ocr(hsvFilterFourPeopleWhite(screenshot))
    result = match_img(screenshot, get_source('hover_normal'), 10, 10, rate)
    if result[3] is not None:
        x, y = result[3]['rectangle'][3]
        mutil_crop(screenshot, hover_list, (x - 230, y + 10), (x + 120, y + 142))
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
                return True
    return False


def rewardMaskNotification(rate=0.9):
    """
    可能是为了保险加的
    :param rate:
    :return:
    """
    outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
    result = match_img(screenshot, get_source('hover_second'), 10, 10, rate, get_source('hover_second_mask'))
    if result[3] is not None:
        x, y = result[3]['rectangle'][3]
        mutil_crop(screenshot, hover_list, (x - 345, y + 15), (x + 5, y + 155))
        return True
    if outs:
        for out in outs:
            text = out['text']
            xs, ys = out['position'][3]
            xs, ys = int(xs), int(ys)
            if ys > 600 or xs < 200 or xs > 850:
                continue
            # print(text)
            if "请选择" in text:
                x, y = out['position'][3]
                x, y = int(x), int(y)
                mutil_crop(screenshot, hover_list, (x, y), (x + 360, y + 140))
                return True
    return False


def __if_have_notification_check(rate=0.95):
    if normalNotification(rate):
        logger.info("检测到普通弹窗")
        return True
    elif rewardNotification(rate):
        logger.info("检测到奖励弹窗1")
        return True
    elif rewardMaskNotification(rate):
        logger.info("检测到奖励弹窗2")
        return True
    else:
        return False


def __auto_click_four_people(rate=0.85):
    # 有弹窗并完成切割返回true 否则false
    if not __if_have_notification_check(rate):
        return
    min_index = hm.model_predict(hover_list)
    # TODO 计算点击坐标(暂时设置为 识别出的切割图片的中心位置)

    predict_images = cv2.imread(hover_list[min_index])
    cv2.imshow("hover", predict_images)
    cv2.waitKey()
    result = match_img(screenshot, hover_list[min_index], 10, 10, 0.95)
    if result[3] is None:
        logger.info("匹配失败弹窗点击失败,需要手动处理")
        save_fight_normal_check(screenshot)
        sound_util.playsound()
        return
    target_x, target_y = result[3]['result']

    if target_x == 0 and target_y == 0:
        logger.info("匹配失败弹窗点击失败,需要手动处理")
        save_fight_normal_check(screenshot)
        sound_util.playsound()
    else:
        logger.info(f'根据预测结果,点击坐标为[x：{target_x} < ; y：{target_y}]')
        # game_mouse.move_click(target_x, target_y)
        # time.sleep(0.5)
        # if __if_have_notification_check(rate):
        #     log_queue.put("匹配失败弹窗点击失败,需要手动处理")
        #     # TODO 收集预测失败的图片
        #     save_fight_normal_check(screen_shot)
        #     sound_util.playsound()


__auto_click_four_people()
