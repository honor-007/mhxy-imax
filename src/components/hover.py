from assets.sources import get_source
from config import hover_list
from script_utils.cnOcr import cn_ocr
from script_utils.grabScreen import winShot
from script_utils.imageTransform import hsvFilterWordWhite, mutil_crop
from script_utils.matchTemplate import match_img
from src.components.window import WINDOW_ID
from src.utils.globalVariable import hover_image_save_path
from src.utils.img_util import save_image, save_fight_normal_check, save_fight_reward_check


class Hover:
    """
    战斗 悬浮窗口解决类
    """

    def __init__(self, hwnd):
        self.hwnd = hwnd

    def __screenshot(self):
        return winShot(self.hwnd)

    def rewardNotification(self, rate=0.9):
        # 1. 截取mhxy的窗口截图
        screenshot = self.__screenshot()
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

    def normalNotification(self, rate=0.9):
        """
        识别是否存在普通弹窗
        :param rate:
        :return:
        """
        screenshot = self.__screenshot()
        outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
        result = match_img(screenshot, get_source('hover_normal'), 10, 10, rate)
        if result[3] is not None:
            x, y = result[3]['rectangle'][3]
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

    def rewardMaskNotification(self, rate=0.9):
        """
        可能是为了保险加的
        :param rate:
        :return:
        """
        screenshot = self.__screenshot()
        outs = cn_ocr.ocr(hsvFilterWordWhite(screenshot))
        result = match_img(screenshot, get_source('hover_second'), 10, 10, rate, get_source('hover_second_mask'))
        if result[3] is not None:
            x, y = result[3]['rectangle'][3]
            mutil_crop(screenshot, hover_list, (x - 350, y + 15), (x + 10, y + 155))
            # TODO 收集训练集用 正式环境删除
            save_image(screenshot, hover_image_save_path)
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
                    # TODO 收集训练集用 正式环境删除
                    save_image(screenshot, hover_image_save_path)
                    return True
        return False


hover = Hover(WINDOW_ID)
