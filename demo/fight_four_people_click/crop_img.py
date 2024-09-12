import os

import cv2
import numpy as np

from config import hover_list
from script_utils.matchTemplate import crop_image_data

basedir = os.path.abspath(os.path.dirname(__file__))
save_path = os.path.join(basedir, 'train_img')
print(save_path)

width, height = 90, 120
color = (52, 34, 23)
image = np.zeros((height, width, 3), np.uint8)
image[:] = color
cv2.imwrite(os.path.join(save_path, 'background.png'), image)
#
# predict_images = cv2.imread(hover_list[0])
# crop_img = crop_image_data(predict_images, left_up=(0, 0), right_down=(87, 132))
#
# cv2.imshow("crop", crop_img)
# confirm = input(f'请确认路径切割的图像是否合适: (确认后输入 Y , 输入其他退出) ')
# k = cv2.waitKey()
#
# if k == ord('y') :
