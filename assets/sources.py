# -*- coding: utf-8 -*-
import json
import os

from script_utils.common_utils import findfiles

basedir = os.path.abspath(os.path.dirname(__file__))

source_path = os.path.join(basedir, 'sources.json')  #
source_datas = json.load(open(source_path, 'r', encoding='utf-8'))


def get_source(source_name):
    """
    根据source.json获取文件路径
    :param source_name:
    :return:
    """
    return os.path.join(basedir, source_datas[source_name]["directory"], source_datas[source_name]["name"])


def load_json(source_name):
    """
    获取json data
    :param source_name:
    :return:
    """
    path = get_source(source_name)
    json_data = json.load(open(path, 'r', encoding='utf-8'))
    return json_data


def write_json(ips, name):
    """
    在指定json文件中写入数据
    :param ips:
    :param name:
    :return:
    """
    filename = get_source(name)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ips, f, indent=4, ensure_ascii=False)


def join_path(directory, name):
    """
    拼接路径 basedir+directory+name
    """
    return os.path.join(basedir, directory, name)


def get_file_path_by_name(directory, file_name):
    path = os.path.join(basedir, directory)
    result = findfiles(path)
    for res in result:
        if res == file_name:
            return os.path.join(path, res)
    raise KeyError


location_data = load_json("location")
proxies_data = load_json("proxies")
npc_data = load_json("npc")
props_data = load_json("props")
move_directory = os.path.join(basedir, 'move')

windows_json = load_json("windows_json")

# 押镖相关 escort.json文件
escort_setting = load_json('escort_setting_json')
# 自动战斗相关json文件
auto_fight_setting = load_json('auto_fight_setting_json')
# 系统设置相关json文件
system_setting = load_json("system_setting_json")

print(get_source("idiom_confirm"))
print(get_source("idiom_reset"))
