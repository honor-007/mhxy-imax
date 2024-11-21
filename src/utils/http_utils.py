import sys
import time
from tkinter.messagebox import showerror

import requests
import json

from src.encrypt.aes import AesEncrypt
from src.utils.globalVariable import log_queue
from src.utils.uuid_util import get_pc_code

# 目标Java程序的URL
base_url = 'http://localhost:8081/api/backend/python/'
key = 'Sixteensbyteskey'
version = 20241024
# characterId = '123456'
aes_util = AesEncrypt(key.encode("utf-8"))


def base_post(url, data):
    data_string = json.dumps(data)
    data_encrypted = aes_util.aes_encrypt(data_string.encode('utf-8'))
    # 发送POST请求
    response = requests.post(url, data=data_encrypted, headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        showerror('连接错误', '无法连接到服务器,请联系管理人员')
        raise Exception('无法连接到服务器')
    result_string = aes_util.aes_decrypt(response.text)
    # 打印响应内容
    # print("【接收到的返回数据】{}", result_string)
    result_json = json.loads(result_string)
    print(result_json['msg'])
    current_timestamp_ms = int(time.time() * 1000)
    if (result_json['code'] == 200 and result_json['success'] is True and 0 < current_timestamp_ms - int(
            result_json['instant']) < 10000):
        return result_json['data']
    else:
        log_queue.put("请求失败")
        showerror("请求失败", "请求失败,请联系管理人员")
        raise Exception('请求失败')


def trial_activation(characterId):
    """
    试用激活
    param:  characterId 角色id
    """
    pc_code = get_pc_code()
    data = {
        'pcCode': pc_code,
        'characterId': characterId
    }
    return base_post(base_url + 'activation/trial-seven-days', data)


def code_activation(activationCode, characterId):
    """
    激活码激活
    param: activationCode 激活码
    param: characterId 角色id
    return:
    """
    pc_code = get_pc_code()
    data = {
        'activationCode': activationCode,
        'characterId': characterId
    }
    return base_post(base_url + 'activation/activate', data)


def check(characterId):
    """
    检查
    :param characterId:
    :return: remainingDuration 剩余时间(天)
    """
    data = {
        'version': version,
        'characterId': characterId
    }
    return base_post(base_url + 'activation/check', data)


# character_id = system_setting['character_id']
# http_response = check(character_id)
# http_response = check('123456')
# print(http_response)
