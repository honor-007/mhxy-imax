import cv2
import numpy as np

from script_utils.matchTemplate import crop_image_data

scale = 20
img = cv2.imread('test1.png')
character_img = crop_image_data(img, (955, 0), (1020, 50))
img = cv2.resize(character_img, (0, 0), fx=scale, fy=scale)

# 转换到HSV空间，因为HSV对于颜色分割更有效
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 定义红色的HSV范围
# 注意：这些值可能需要根据你的图像进行调整
# lower_red = np.array([0, 79, 60])
# upper_red = np.array([10, 255, 255])

lower_red = np.array([0, 113, 79])
upper_red = np.array([24, 255, 255])
mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

lower_red = np.array([170, 150, 100])
upper_red = np.array([180, 255, 255])
mask2 = cv2.inRange(img_hsv, lower_red, upper_red)

# 合并两个掩模
mask = mask1 + mask2

cv2.imshow("mask", mask)
cv2.waitKey()
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
    cv2.drawContours(img, [c], -1, (0, 255, 0), 3)
    for pt in points:
        cv2.circle(img, pt, 5, (0, 0, 255), -1)

    cv2.imshow("Detected Rectangle", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(x / scale, y / scale, w / scale, h / scale)