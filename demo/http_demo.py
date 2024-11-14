import time

import requests
import json

from src.encrypt.aes import AesEncrypt
from src.utils.uuid_util import get_pc_code

# 目标Java程序的URL
base_url = 'http://localhost:8081/api/backend/python/'
key = 'Sixteensbyteskey'
version = 20241024
characterId = '123456'
aes_util = AesEncrypt(key.encode("utf-8"))


def base_post(url, data):
    data_string = json.dumps(data)
    data_encrypted = aes_util.aes_encrypt(data_string.encode('utf-8'))
    # 发送POST请求
    response = requests.post(url, data=data_encrypted, headers={'Content-Type': 'application/json'})
    result_string = aes_util.aes_decrypt(response.text)
    # 打印响应内容
    # print("【接收到的返回数据】{}", result_string)
    result_json = json.loads(result_string)
    print(result_json['msg'])
    current_timestamp_ms = int(time.time() * 1000)
    if (result_json['code'] == 200 and result_json['success'] == True and 0 < current_timestamp_ms - int(
            result_json['instant']) < 10000):
        return result_json['data']
    else:
        return 0


def trial_activation():
    """
    试用激活
    """
    pc_code = get_pc_code()
    data = {
        'pcCode': pc_code,
        'characterId': characterId
    }
    result = base_post(base_url + 'activation/trial-seven-days', data)
    if result != 0:
        print("【接收到的返回数据】{}", result)


def code_activation(activationCode,characterId):
    """
    激活码激活
    """
    pc_code = get_pc_code()
    data = {
        'activationCode': activationCode,
        'characterId': characterId
    }
    result = base_post(base_url + 'activation/activate', data)
    if result != 0:
        print("【接收到的返回数据】{}", result)


def check():
    data = {
        'version': version,
        'characterId': characterId
    }
    result = base_post(base_url + 'activation/check', data)
    if result != 0:
        print(f"剩余时长(小时):{result['remainingDuration']}")
    else:
        print(f"版本检查未通过{result}")


def test():
    data = {
        'biosUuid': 'value1',
        'biosSerialNo': 'value2',
        'instant': 12341535345
    }
    result = base_post(base_url + 'activation/test', data)
    if result != 0:
        print("【接收到的返回数据】{}", result)


# test()
# trial_activation()
# check()
code_activation('da4df445-644b-4558-aee4-060474c46e33',characterId)