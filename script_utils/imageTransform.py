import cv2
import numpy as np


def hsvFilter(img_src, hsv, mask=True, scale=2):
    """
    给出一张图片，根据hsv值，筛选出需要颜色
    :param img_src:
    :param hsv:
    :param mask: True 将返回掩码图
    :param scale:
    :return:
    """
    if not isinstance(img_src, np.ndarray):
        img = cv2.imread(img_src)
    else:
        img = img_src
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_min, h_max, s_min, s_max, v_min, v_max = hsv
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask_ = cv2.inRange(img_hsv, lower, upper)
    img_result = cv2.bitwise_and(img, img, mask=mask_)
    if mask:
        return cv2.resize(mask_, (0, 0), fx=scale, fy=scale)
    else:
        return cv2.resize(img_result, (0, 0), fx=scale, fy=scale)


def hsvFilterErrorYellow(img_src, mask=True, scale=10):
    """
    梦幻西游中的浅黄色字体，如弹窗点击次数过多后的提示"你错误操作多次，请重启游戏"
    :param img_src:
    :param mask:
    :param scale:
    :return:
    """
    hsv = [0, 45, 207, 255, 37, 255]
    return hsvFilter(img_src, hsv, mask, scale)


def hsvFilterTaskRed(img_src, mask=True, scale=5):
    """
    梦幻西游中的红色字体，如领取任务后，任务中高亮的红色信息
    :param img_src:
    :param mask:
    :param scale:
    :return:
    """
    hsv = [0, 1, 70, 255, 0, 255]
    return hsvFilter(img_src, hsv, mask, scale)


def hsvFilterWordWhite(img_src, mask=True, scale=5):
    """
    筛选梦幻西游中的白色字体，如弹窗上出现的白色字体可以被筛选
    :param img_src:
    :param mask:
    :param scale:
    :return:
    """
    hsv = [0, 179, 0, 30, 191, 255]
    return hsvFilter(img_src, hsv, mask, scale)


def hsvFilterLocationWhite(img_src, mask=True, scale=5):
    """
    梦幻西游中的白色字体，左上脚的地图信息
    :param img_src:
    :param mask:
    :param scale:
    :return:
    """
    hsv = [0, 179, 0, 33, 52, 255]
    return hsvFilter(img_src, hsv, mask, scale)


def mutil_crop(source, name_list, left_up, right_down, is_save=True):
    """
    根据 name_list的长度，将source图片均分 并保存到name_list中的对应位置
    :param source:
    :param name_list:
    :param left_up:
    :param right_down:
    :param is_save:
    :return:
    """
    if not isinstance(source, np.ndarray):
        img = cv2.imread(source)
    else:
        img = source
    step = (right_down[0] - left_up[0]) // len(name_list)
    left_x = left_up[0]
    temp = []
    for name in name_list:
        right_x = left_x + step
        img1 = img[left_up[1]:right_down[1], left_x:right_x]
        temp.append(img1)
        if is_save:
            cv2.imwrite(name, img1)
        left_x = right_x
    return temp


def get_hp_rect(img_src, scale=20.0):
    # 读取图像
    if not isinstance(img_src, np.ndarray):
        img = cv2.imread(img_src)
    else:
        img = img_src
    if img is None:
        print("Error: Image not found.")
        return

    img = cv2.resize(img, (0, 0), fx=scale, fy=scale)

    # 转换到HSV空间，因为HSV对于颜色分割更有效
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 定义红色的HSV范围
    # 注意：这些值可能需要根据你的图像进行调整
    lower_red = np.array([0, 79, 60])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

    lower_red = np.array([170, 120, 0])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(img_hsv, lower_red, upper_red)

    # 合并两个掩模
    mask = mask1 + mask2

    # 查找轮廓
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 假设最大的轮廓是我们想要的红色矩形
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        # print(f"x坐标:{x},y坐标:{y},宽:{w},高:{h}")
        # print(f"x坐标:{x / scale},y坐标:{y / scale},宽:{w / scale},高:{h / scale}")
        # 四个顶点的坐标
        points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        # 显示结果
        # cv2.drawContours(img, [c], -1, (0, 255, 0), 3)
        # for pt in points:
        #     cv2.circle(img, pt, 5, (0, 0, 255), -1)
        #
        # cv2.imshow("Detected Rectangle", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return x / scale, y / scale, w / scale, h / scale


def get_mp_rect(img_src, scale=20.0):
    # 读取图像
    if not isinstance(img_src, np.ndarray):
        img = cv2.imread(img_src)
    else:
        img = img_src
    if img is None:
        print("Error: Image not found.")
        return

    img = cv2.resize(img, (0, 0), fx=scale, fy=scale)

    # 转换到HSV空间，因为HSV对于颜色分割更有效
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 定义红色的HSV范围
    # 注意：这些值可能需要根据你的图像进行调整
    lower_blue = np.array([103, 135, 64])
    upper_blue = np.array([142, 255, 255])
    mask = cv2.inRange(img_hsv, lower_blue, upper_blue)

    # 查找轮廓
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 假设最大的轮廓是我们想要的红色矩形
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        # print(f"x坐标:{x},y坐标:{y},宽:{w},高:{h}")
        # print(f"x坐标:{x / scale},y坐标:{y / scale},宽:{w / scale},高:{h / scale}")

        # 四个顶点的坐标
        points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

        # 显示结果
        # cv2.drawContours(img, [c], -1, (0, 255, 0), 3)
        # for pt in points:
        #     cv2.circle(img, pt, 5, (0, 0, 255), -1)
        # cv2.imshow("mp", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return x / scale, y / scale, w / scale, h / scale
