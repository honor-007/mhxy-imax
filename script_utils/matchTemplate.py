import cv2
import numpy
import numpy as np
from skimage.metrics import structural_similarity

DEBUG = False


def find_template(im_source, im_search, threshold=0.5, rgb=False, bgremove=False, mask=None, method=None):
    """
    @return find location
    if not found; return None
    """
    result = find_all_template(im_source, im_search, threshold, 1, rgb, bgremove, mask, method)
    return result[0] if result else None


def find_all_template(im_source, im_search, threshold=0.5, maxcnt=0, rgb=False, bgremove=False, mask=None, method=None):
    """
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        im_source(string): 图像、素材
        im_search(string): 需要查找的图片
        threshold: 阈值，当相识度小于该阈值的时候，就忽略掉

    Returns:
        A tuple of found [(point, score), ...]
        例如:
        ---result[3]---
        {'result': (89.0, 571.5), 'rectangle': ((5, 516), (5, 627), (173, 516), (173, 627)), 'confidence': 0.9998666048049927, 'shape': (900, 693)}
            result:检出图像在模板中的中心坐标
            rectangle:检测出来的图像在模板中的四个顶点坐标
            confidence:相似度
            shape:模板大小

    Raises:
        IOError: when file read error
        :param method:
        :param bgremove:
        :param rgb:
        :param im_source:
        :param im_search:
        :param threshold:
        :param maxcnt:
    """
    # print(type(im_source), type(im_search), type(mask))
    # method = cv2.TM_CCORR_NORMED
    # method = cv2.TM_SQDIFF_NORMED
    cv2_method = cv2.TM_CCOEFF_NORMED
    if method is not None:
        cv2_method = method

    if rgb:
        s_bgr = cv2.split(im_search)  # Blue Green Red
        i_bgr = cv2.split(im_source)
        weight = (0.3, 0.3, 0.4)
        resbgr = [0, 0, 0]
        for i in range(3):  # bgr
            resbgr[i] = cv2.matchTemplate(i_bgr[i], s_bgr[i], cv2_method, mask=mask)
        res = resbgr[0] * weight[0] + resbgr[1] * weight[1] + resbgr[2] * weight[2]
    else:
        s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGR2GRAY)
        i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGR2GRAY)
        # 边界提取(来实现背景去除的功能)
        if bgremove:
            s_gray = cv2.Canny(s_gray, 100, 200)
            i_gray = cv2.Canny(i_gray, 100, 200)

        res = cv2.matchTemplate(i_gray, s_gray, cv2_method, mask=mask)
    w, h = im_search.shape[1], im_search.shape[0]

    result = []
    while True:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if cv2_method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        if DEBUG:
            print('templmatch_value(thresh:%.1f) = %.3f' % (threshold, max_val))  # not show debug
        if max_val < threshold:
            break
        # calculator middle point
        middle_point = (top_left[0] + w / 2, top_left[1] + h / 2)
        result.append(dict(
            result=middle_point,
            rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]),
                       (top_left[0] + w, top_left[1] + h)),
            confidence=max_val
        ))
        if maxcnt and len(result) >= maxcnt:
            break
        # floodfill the already found area
        cv2.floodFill(res, None, max_loc, (-1000,), max_val - threshold + 0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
    return result


def match_img(img_src, img_obj, phone_x, phone_y, confidence_value=0.0, mask=None, method=None):
    """
    在源图像中查找模板图像，并将匹配位置映射到实际设备屏幕坐标。

    核心流程：
        1. 将输入图像统一转换为 numpy 数组格式
        2. 调用 find_template 进行模板匹配，获取匹配位置和置信度
        3. 根据源图像尺寸与设备屏幕尺寸的比例，将匹配坐标映射为设备上的实际坐标

    :param img_src: 源图像（截屏图），可以是文件路径(str)或已加载的图像数据(numpy.ndarray)
    :param img_obj: 模板图像（要查找的目标小图），可以是文件路径(str)或已加载的图像数据(numpy.ndarray)
    :param phone_x: 设备屏幕的实际宽度（像素），用于坐标映射
    :param phone_y: 设备屏幕的实际高度（像素），用于坐标映射
    :param confidence_value: 匹配置信度阈值，低于此值的匹配结果将被忽略，默认0.0
    :param mask: 掩码图像，用于非矩形区域的模板匹配，可以是文件路径(str)或numpy.ndarray，默认None
    :param method: cv2模板匹配算法，如cv2.TM_CCOEFF_NORMED等，默认None（使用TM_CCOEFF_NORMED）
    :return: 四元组 (position_x, position_y, confidence_str, match_result)
            - position_x: 匹配位置映射到设备屏幕后的x坐标（int），未匹配时为None
            - position_y: 匹配位置映射到设备屏幕后的y坐标（int），未匹配时为None
            - confidence_str: 置信度字符串，截取前4个字符（如"0.99"），未匹配时为None
            - match_result: 完整匹配结果字典，包含以下字段，未匹配时为None
                - 'result': (x, y) 模板在源图像中的中心坐标
                - 'rectangle': 四顶点坐标 (左上, 左下, 右上, 右下)
                - 'confidence': 匹配置信度浮点数
                - 'shape': (width, height) 源图像的宽高
    """
    # 如果传入的是文件路径字符串，则通过cv2读取为numpy数组
    if not isinstance(img_src, numpy.ndarray):
        img_src = cv2.imread(img_src)
    if not isinstance(img_obj, numpy.ndarray):
        img_obj = cv2.imread(img_obj)

    # 处理掩码参数：None则不使用掩码，路径则以灰度模式读取，数组则直接使用
    if mask is None:
        img_mask = mask
    else:
        if not isinstance(mask, numpy.ndarray):
            img_mask = cv2.imread(mask, 0)  # 以灰度模式读取掩码图
        else:
            img_mask = mask

    # 调用 find_template 执行模板匹配，返回最佳匹配结果（单个dict或None）
    match_result = find_template(img_src, img_obj, confidence_value, rgb=False, mask=img_mask, method=method)

    if match_result is not None:
        # 记录源图像的宽高到匹配结果中（shape[0]是高度，shape[1]是宽度）
        match_result['shape'] = (img_src.shape[1], img_src.shape[0])
        # 获取模板在源图像中匹配到的中心坐标
        x, y = match_result['result']
        # 获取源图像的宽高（整数）
        shape_x, shape_y = tuple(map(int, match_result['shape']))
        # 按比例将源图像中的坐标映射到实际设备屏幕坐标
        # 公式：设备坐标 = 设备尺寸 * (源图像中的坐标 / 源图像尺寸)
        position_x, position_y = int(phone_x * (x / shape_x)), int(phone_y * (y / shape_y))
    else:
        # 未找到匹配结果，返回四个None
        return None, None, None, None

    return position_x, position_y, str(match_result['confidence'])[:4], match_result


def match_all_img(img_src, img_obj, phone_x, phone_y, confidence_value=0.0, mask=None,
                  method=None):  # img_src=原始图像，img_obj=待查找的图片
    if not isinstance(img_src, numpy.ndarray):
        img_src = cv2.imread(img_src)
    if not isinstance(img_obj, numpy.ndarray):
        img_obj = cv2.imread(img_obj)
    if mask is None:
        img_mask = mask
    else:
        if not isinstance(mask, numpy.ndarray):
            img_mask = cv2.imread(mask, cv2.COLOR_BGR2GRAY)
        else:
            img_mask = mask
    match_result = find_all_template(img_src, img_obj, confidence_value, maxcnt=1, rgb=False, mask=img_mask,
                                     method=method)
    print(match_result)
    return match_result


def take_red_line(result, image, name):
    """
    模板匹配后的结果进行二次绘图，标出模板匹配位置
    :param result:
    :param image: 原图片
    :param name: 保存的图片名
    :return:
    """
    rectangle = result[3]["rectangle"]
    x_min = rectangle[0][0]
    y_min = rectangle[0][1]
    x_max = rectangle[2][0]
    y_max = rectangle[3][1]

    if not isinstance(image, numpy.ndarray):
        image = cv2.imread(image)
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)
    cv2.imwrite(name, image)


def compare_image(image_a, image_b, channel_axis=True):
    """
    对图片A 和 图片B的相似度进行计算，0为最低，1为最大
    :param image_a: 图片A
    :param image_b: 图片B
    :param channel_axis:
    :return: 相似度得分
    """
    if not isinstance(image_a, numpy.ndarray):
        image_a = cv2.imread(image_a)
    if not isinstance(image_b, numpy.ndarray):
        image_b = cv2.imread(image_b)
    gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
    (score, diff) = structural_similarity(gray_a, gray_b, full=True, channel_axis=channel_axis)
    return score


def crop_image_data(image_data, left_up, right_down):
    """
    :param image_data: 裁剪的图片，类型为numpy.ndarray
    :param left_up: 裁剪的左上顶点
    :param right_down: 裁剪的右下顶点
    :return:裁剪后的图像
    """
    if not isinstance(image_data, np.ndarray):
        image_data = cv2.imread(image_data)
    img = image_data[int(left_up[1]):int(right_down[1]), int(left_up[0]):int(right_down[0])]
    return img



