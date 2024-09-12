import os

import tensorflow as tf
from tensorflow import keras
from game_models.source import get_model
from script_utils.loggerConfig import logger

"""
[点击面对着你的人物]弹窗预测模型
"""
AUTOTUNE = tf.data.experimental.AUTOTUNE

model = None

# IMG_HEIGHT = 140
# IMG_WIDTH = 90
IMG_HEIGHT = 100
IMG_WIDTH = 100


def model_load():
    logger.info('模型读取')
    logger.info('模型路径为:{}'.format(get_model('four_people')))
    global model
    model = keras.models.load_model(get_model('four_people'))
    # model = keras.models.load_model(r'E:\workspace\python_project\mhxy-imax\dist\main\_internal\game_models\model\mhxy.h5')
    model.summary()


def model_predict(imgs, use_paths=True):
    logger.info('模型预测')
    global model
    if use_paths:
        imgs = [load_and_preprocess_image(path) for path in imgs]
        # print(imgs)
    imgs = tf.convert_to_tensor(imgs)
    predictions = model.predict(imgs)
    predictions = [row[0] for row in predictions]
    logger.info(predictions)
    min_index = predictions.index(min(predictions))
    logger.info(f' 预测结果为 第 [ {min_index + 1} ] 张图片')
    return min_index


def model_predict_tool(img):
    logger.info('模型预测')
    img = [load_and_preprocess_image(img)]
    imgs = tf.convert_to_tensor(img)
    predictions = model.predict(imgs)
    predictions = [row[0] for row in predictions]
    return predictions[0]


def preprocess_image(image):
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [IMG_HEIGHT, IMG_WIDTH])
    image /= 255.0  # normalize to [0,1] range
    return image


def load_and_preprocess_image(path):
    image = tf.io.read_file(path)
    return preprocess_image(image)


model_load()

if __name__ == '__main__':
    model_load()
    print(model_predict_tool(r"E:\workspace\python_project\mhxy-imax\img.png"))
