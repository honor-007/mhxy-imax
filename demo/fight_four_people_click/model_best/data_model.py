from script_utils.loggerConfig import logger
from tensorflow import keras
import tensorflow as tf

model = None
IMG_HEIGHT = 100
IMG_WIDTH = 100


def model_load():
    logger.info('模型读取')
    print(r'mhxy_140_90.h5')
    global model
    model = keras.models.load_model(
        r'E:\workspace\python_project\mhxy-imax\demo\fight_four_people_click\model_best\mhxy.h5')
    model.summary()


def model_predict(imgs, use_paths=True):
    logger.info('模型预测')
    global model
    if use_paths:
        imgs = [load_and_preprocess_image(path) for path in imgs]
        print(imgs)
    imgs = tf.convert_to_tensor(imgs)
    predictions = model.predict(imgs)
    predictions = [row[0] for row in predictions]
    logger.info(predictions)
    min_index = predictions.index(min(predictions))
    logger.info(f' 预测结果为 第 [ {min_index + 1} ] 张图片')
    return min_index


def preprocess_image(image):
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [IMG_HEIGHT, IMG_WIDTH])
    image /= 255.0  # normalize to [0,1] range
    return image


def load_and_preprocess_image(path):
    image = tf.io.read_file(path)
    return preprocess_image(image)


model_load()
