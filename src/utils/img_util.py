import datetime
import os
import cv2


def save_image(img, folder_path=r'E:\temp'):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        # 创建文件夹
        os.makedirs(folder_path)

    now = datetime.datetime.now()
    formatted_time = now.strftime('%Y-%m-%d_%H:%M:%S') + ".png"
    img_path = os.path.join(folder_path, formatted_time)

    cv2.imwrite(img_path, img)
