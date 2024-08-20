import random


def random_button_coordinate(rectangle):
    """
    随机要点击按钮的坐标
    :return:
    """
    if rectangle:
        x = random.randint(rectangle[0][0]+10, rectangle[2][0]-10)
        y = random.randint(rectangle[0][1]+5, rectangle[1][1]-5)
        return (x, y)
    return None
