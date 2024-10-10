import datetime
import os

import cv2

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_dir = os.path.dirname(current_file_path)
# 假设项目目录是demo.py的上一级目录
basedir = os.path.dirname(os.path.dirname(current_dir))
train_path = os.path.join(basedir, 'train_set')

def save_escort_task_check(img):
    now = datetime.datetime.now()
    img_name = now.strftime('%Y-%m-%d_%H-%M-%S') + ".png"
    save_path = os.path.join(train_path, 'escort_task_check',  img_name)
    cv2.imwrite(save_path, img)

def save_fight_normal_check(img):
    now = datetime.datetime.now()
    img_name = now.strftime('%Y-%m-%d_%H-%M-%S') + ".png"
    save_path = os.path.join(train_path, 'fight_four_people_normal',  img_name)
    cv2.imwrite(save_path, img)

def save_fight_reward_check(img):
    now = datetime.datetime.now()
    img_name = now.strftime('%Y-%m-%d_%H-%M-%S') + ".png"
    save_path = os.path.join(train_path, 'fight_four_people_reward',  img_name)
    cv2.imwrite(save_path, img)


# img = cv2.imread('**.png')
# save_fight_normal_check(img)
# save_fight_reward_check(img)