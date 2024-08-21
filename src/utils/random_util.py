import random


def random_button_coordinate(rectangle):
    """
    随机要点击按钮的坐标
    :return:
    """
    if rectangle:
        x = random.randint(rectangle[0][0], rectangle[2][0])
        y = random.randint(rectangle[0][1], rectangle[1][1])
        return (x, y)
    return None
