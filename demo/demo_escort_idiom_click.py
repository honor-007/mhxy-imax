import os
import random
import threading
import time
from numpy import mean
import cv2
import numpy as np
from assets.sources import get_source, location_data
from script_utils.cnOcr import cn_ocr, get_chinese_text, get_closed_string, find_text
from script_utils.imageTransform import hsvFilterLocationWhite, hsvFilterWordWhite
from script_utils.loggerConfig import logger
from script_utils.matchTemplate import match_img, crop_image_data, compare_image
from script_utils.siamese_compare import detect_words, compare_siamese
from siamese_utils.idiom import get_idiom
from siamese_utils.verification_code import make_mock_picture


# img = crop_image_data('test9.png', left_up=(300, 150), right_down=(770, 300))
# cv2.imshow("221", img)
# cv2.waitKey()
#
# move_corp_sceenshot = hsvFilterWordWhite(img)
# h, w = move_corp_sceenshot.shape
# resize_img = cv2.resize(move_corp_sceenshot, (int(w / 2), int(h / 2)), interpolation=cv2.INTER_AREA)
# cv2.imshow("22", resize_img)
# cv2.waitKey()
#
# result_word = find_text(move_corp_sceenshot, ["鼠标", "点选"])
# print(result_word)


def is_have_check(img=None):
    """
    :return:
    :return:
    0 移动弹窗, 1 成语弹窗

    """
    screenshot = cv2.imread("test9.png")
    move_corp_sceenshot = hsvFilterWordWhite(crop_image_data(screenshot, left_up=(300, 150), right_down=(770, 300)))
    result_word = find_text(move_corp_sceenshot, ["鼠标", "点选"])
    result_chengyu = match_img(screenshot, get_source("idiom_confirm"), 10, 10, 0.92)
    result_cheng_yu_reset = match_img(screenshot, get_source("idiom_reset"), 10, 10, 0.95)[3]
    if result_word is not None or result_chengyu[3] is not None or result_cheng_yu_reset is not None:
        # TODO 收集训练集用 正式环境删除
        basedir = os.path.abspath(os.path.dirname(__file__))
        timestamp = time.time()
        source_path = os.path.join(basedir, '../train_set', "escort_task_check", f"{timestamp}.png")
        cv2.imwrite(source_path, screenshot)

        if result_word is not None:
            leftup = (result_word[0], result_word[1] - 180)
            # right = result_word[1] + 41
            # save_path = os.path.join(c.check_move_word_dir, utils_local.time_str() + '.jpg')
            # fi.crop(screenshot, save_path, leftup=leftup, rihgtdown=(leftup[0] + 350, leftup[1] + 150))
            return 0, [leftup, (leftup[0] + 350, leftup[1] + 150)]
        if result_chengyu[3] is not None:
            # save_path = os.path.join(c.check_chengyu_dir, utils_local.time_str() + '.jpg')
            leftup = result_chengyu[3]['rectangle'][1]
            # fi.crop(screenshot, save_path, leftup=(leftup[0] - 170, leftup[1] - 170),
            #         rihgtdown=(leftup[0] + 100, leftup[1] - 110))

            # take_red_line(result_word, c.check_screenshot, '{}.png'.format(3))
            return 1, [(leftup[0] - 170, leftup[1] - 170), (leftup[0] + 100, leftup[1] - 110)]
        if result_cheng_yu_reset is not None:
            # save_path = os.path.join(c.check_chengyu_dir, utils_local.time_str() + '.jpg')
            reset_xy = result_cheng_yu_reset['rectangle'][1]
            leftup = (reset_xy[0] - 105, reset_xy[1])
            # fi.crop(screenshot, save_path, leftup=(leftup[0] - 170, leftup[1] - 170),
            #         rihgtdown=(leftup[0] + 100, leftup[1] - 110))
            return 1, [(leftup[0] - 170, leftup[1] - 170), (leftup[0] + 100, leftup[1] - 110)]
        return
    else:
        return


def get_title_from_shot(rectangle):
    left_up = rectangle[0]
    right_down = rectangle[1]
    crop_img = crop_image_data('test9.png', left_up=(left_up[0], left_up[1] - 120),
                               right_down=(right_down[0] + 180, right_down[1] - 95))
    cv2.imshow("get_title_from_shot", crop_img)
    cv2.waitKey()
    return get_idiom(crop_img)


def get_chengyu_from_shot(rectangle):
    img = crop_image_data('test9.png', left_up=rectangle[0],
                          right_down=rectangle[1])

    # cv2.imshow("get_chengyu_from_shot", img)
    # cv2.waitKey()

    return img


WORD_IMAGE = {}


def load_word_img_to_memory(words):
    """

    :param words:
    :return:
    """
    logger.info("生成加载文字图片,使用mock方式")
    for word in words:
        WORD_IMAGE[word] = make_mock_picture(word, save_dir=None, num=3)


def clc_word_value(img, words):
    """
    计算一个词语 与这个图片的关联性
    :param img:
    :param words:
    :return:
    """
    load_word_img_to_memory(words)

    templates = detect_words(img, count=4)
    result = []
    for k in range(len(templates)):
        template_img = crop_image_data(img, left_up=templates[k][0], right_down=templates[k][1])
        temp = []
        for word in words:
            # word_dir = os.path.join(dir_path, word)
            word_img_list = WORD_IMAGE[word]
            similarity = 0
            for s in word_img_list:
                clc_similarity = compare_siamese(template_img, s)
                if clc_similarity > similarity:
                    similarity = clc_similarity
            # print("第{}图,在--{}--上,最大的相似度为:{}".format(k,word,similarity))
            temp.append(similarity)
        result.append(max(temp))
    return mean(result)


def get_index_by_word(crops_img, word):
    temp = []
    templates = detect_words(crops_img, count=4)
    for k in range(len(templates)):
        template_img = crop_image_data(crops_img, left_up=templates[k][0], right_down=templates[k][1])
        word_img_list = WORD_IMAGE[word]
        similarity = 0
        for img in word_img_list:
            clc_similarity = compare_siamese(template_img, img)
            if clc_similarity > similarity:
                similarity = clc_similarity
        logger.info("get_index_by_word第{}张图在--{}--上,相似度为:{}".format(k, word, similarity))
        temp.append(similarity)
    index = temp.index(max(temp))
    return index


def get_word(wrod_img, words, num):
    temp = []
    for word in words:
        # word_dir = os.path.join(dir_path, word)
        word_img_list = WORD_IMAGE[word]
        similarity = 0
        for img in word_img_list:
            clc_similarity = compare_siamese(wrod_img, img)
            if clc_similarity > similarity:
                similarity = clc_similarity
        logger.info("get_word第{}张图在--{}--上,相似度为:{}".format(num, word, similarity))
        temp.append(similarity)
    index = temp.index(max(temp))
    return words[index]


def get_words(crops_img, words):
    result = ''
    templates = detect_words(crops_img, count=4)
    for k in range(len(templates)):
        template_img = crop_image_data(crops_img, left_up=templates[k][0], right_down=templates[k][1])
        word = get_word(template_img, words, num=k)
        result += word
    return result


def is_has_two(word, words):
    count = 0
    for i in words:
        if i == word:
            count += 1
    if count == 1:
        return False
    else:
        return True


def clcik_chengyu(rectangle):
    """
    :param rectangle: 图片的坐标
    :return:
    """
    # 文字识别中，所有的成语组成的list
    titles = get_title_from_shot(rectangle)
    logger.info(titles)
    chengyu_img = get_chengyu_from_shot(rectangle)

    res = []
    for t in titles:
        res.append(clc_word_value(chengyu_img, t))
    while len(res) == 0:
        logger.info("未在标题中找到四字词语，重试中......")
        titles = get_title_from_shot(rectangle)
        logger.info(titles)
        chengyu_img = get_chengyu_from_shot(rectangle)

        res = []
        for t in titles:
            res.append(clc_word_value(chengyu_img, t))
    if max(res) == 0:
        logger.info("点选字符{} 至少有一个字不在数据库中".format(titles))
        return
    template = titles[res.index(max(res))]
    logger.info(template)
    for correct_word in template:
        pre_click_img = get_chengyu_from_shot(rectangle)
        words = get_words(chengyu_img, template)
        # 特殊处理 如果有两个气字 说明荡气回肠处理有问题

        logger.info("-------{}-------------".format(words))
        if correct_word not in words:
            logger.info("文字识别不准确, 概率性点击")
            index = get_index_by_word(chengyu_img, correct_word)
            # return
        else:
            index = words.index(correct_word)
        re = detect_words(chengyu_img, count=4)
        word_rectange = np.array(re)[index]
        x = (word_rectange[0][0] + word_rectange[1][0]) / 2 + rectangle[0][0]
        y = (word_rectange[0][1] + word_rectange[1][1]) / 2 + rectangle[0][1]
        # game_mouse.move_click(x, y)
        print(f"1游戏鼠标点击({x},{y})")
        # game_mouse.move(random.uniform(10, 700), random.uniform(10, 100))
        print(f"1游戏鼠标移动到({random.uniform(10, 700)},{random.uniform(10, 100)})")
        chengyu_img = get_chengyu_from_shot(rectangle)

        # 点击后图片未变化，表示点击了重复数字
        if is_has_two(correct_word, template):
            logger.info("存在重复数字:{}".format(correct_word))
            rate = compare_image(pre_click_img, chengyu_img, channel_axis=True)
            if rate > 0.99:
                logger.info('点击前后图片无变化')
                words = list(words)
                words[index] = "0"
                words = ''.join(words)
                if correct_word not in words:
                    # game_mouse.move(random.uniform(10, 700), random.uniform(10, 100))
                    print(f"游戏鼠标移动到({random.uniform(10, 700)},{random.uniform(10, 100)})")
                    return "rest"
                index = words.index(correct_word)
                re = detect_words(chengyu_img, count=4)
                word_rectange = np.array(re)[index]
                x = (word_rectange[0][0] + word_rectange[1][0]) / 2 + rectangle[0][0]
                y = (word_rectange[0][1] + word_rectange[1][1]) / 2 + rectangle[0][1]
                # game_mouse.move_click(x, y)
                print(f"2游戏鼠标点击({x},{y})")
                # game_mouse.move(random.uniform(10, 700), random.uniform(10, 100))
                print(f"2游戏鼠标移动到({random.uniform(10, 700)},{random.uniform(10, 100)})")
                chengyu_img = get_chengyu_from_shot(rectangle)

    confirm_x = rectangle[0][0] + 170 + 25
    confirm_y = rectangle[0][1] + 170 - 10
    # game_mouse.move_click(confirm_x, confirm_y)
    print(f"3游戏鼠标点击({confirm_x},{confirm_y})")
    # game_mouse.move(random.uniform(10, 700), random.uniform(10, 100))
    print(f"3游戏鼠标移动到({random.uniform(10, 700)},{random.uniform(10, 100)})")


cheng_yu_retry = 3
flag = False
screenshot = cv2.imread("test9.png")
move_corp_sceenshot = hsvFilterWordWhite(crop_image_data(screenshot, left_up=(148, 41), right_down=(701, 280)))
result_word = find_text(move_corp_sceenshot, ["鼠标", "点选"])
result_chengyu = match_img(screenshot, get_source("idiom_confirm"), 10, 10, 0.92)
result_cheng_yu_reset = match_img(screenshot, get_source("idiom_reset"), 10, 10, 0.95)[3]
if result_word is not None or result_chengyu[3] is not None or result_cheng_yu_reset is not None:
    if result_word is not None:
        leftup = (result_word[0], result_word[1] - 180)
        # right = result_word[1] + 41
        # save_path = os.path.join(c.check_move_word_dir, utils_local.time_str() + '.jpg')
        # fi.crop(screenshot, save_path, leftup=leftup, rihgtdown=(leftup[0] + 350, leftup[1] + 150))
        check_result = 0, [leftup, (leftup[0] + 350, leftup[1] + 150)]
    if result_chengyu[3] is not None:
        # save_path = os.path.join(c.check_chengyu_dir, utils_local.time_str() + '.jpg')
        leftup = result_chengyu[3]['rectangle'][1]
        # fi.crop(screenshot, save_path, leftup=(leftup[0] - 170, leftup[1] - 170),
        #         rihgtdown=(leftup[0] + 100, leftup[1] - 110))

        # take_red_line(result_word, c.check_screenshot, '{}.png'.format(3))
        check_result = 1, [(leftup[0] - 170, leftup[1] - 170), (leftup[0] + 100, leftup[1] - 110)]
    if result_cheng_yu_reset is not None:
        # save_path = os.path.join(c.check_chengyu_dir, utils_local.time_str() + '.jpg')
        reset_xy = result_cheng_yu_reset['rectangle'][1]
        leftup = (reset_xy[0] - 105, reset_xy[1])
        # fi.crop(screenshot, save_path, leftup=(leftup[0] - 170, leftup[1] - 170),
        #         rihgtdown=(leftup[0] + 100, leftup[1] - 110))
        check_result = 1, [(leftup[0] - 170, leftup[1] - 170), (leftup[0] + 100, leftup[1] - 110)]

    if check_result is not None:
        have_check = True
        tan_type = check_result[0]
        rectangle = check_result[1]

    # 点击成语弹窗
    if tan_type == 1:
        if flag and cheng_yu_retry <= 0:
            print(f"出现[成语弹窗],已经尝试{cheng_yu_retry}次点击,请尽快手动处理,处理后请点击已处理按钮")

        else:
            flag = True
            result = clcik_chengyu(rectangle)
            if result != "rest":
                cheng_yu_retry = cheng_yu_retry - 1
            time.sleep(3)
            check_result = is_have_check()
            if check_result is not None:
                reset_x = rectangle[0][0] + 170 + 25 + 100
                reset_y = rectangle[0][1] + 170 - 10
                # game_mouse.move_click(reset_x, reset_y)
                print(f"4游戏鼠标点击({reset_x},{reset_y})")
                # game_mouse.move(random.uniform(10, 700), random.uniform(10, 100))
                print(f"4游戏鼠标移动到({random.uniform(10, 700)},{random.uniform(10, 100)})")
                have_check = True
            else:
                have_check = False
