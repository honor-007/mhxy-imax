import cv2

from assets.sources import get_source
from script_utils.matchTemplate import match_img, crop_image_data

screen = cv2.imread('test14.png')
result = match_img(screen, get_source("disable_mouse"), 10, 10, 0.95)[3]
if result is not None:
    print(result)
else:
    print("sssss")
# rectangle = result[3]['rectangle']
# img = crop_image_data(screen, rectangle[0], rectangle[3])
# cv2.imshow("22", img)
# cv2.waitKey()
