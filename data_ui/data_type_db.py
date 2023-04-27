# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 16:21
# @Author  : XXX
# @Site    : 
# @File    : data_type_db.py
# @Software: PyCharm 
# @Comment :
import numpy as np

DATA_TYPE_DB = [
    {'name': '速度-RMS均', 'is_v': 'V', 'address': [0, 1, 2]},
    {'name': '温度', 'is_v': 'S', 'address': [3]},
    {'name': '加速度-RMS均', 'is_v': 'V', 'address': [4, 5, 6]},
    {'name': '速度-MAX峰', 'is_v': 'V', 'address': [7, 11, 15]},
    {'name': '速度-峭度均', 'is_v': 'V', 'address': [8, 12, 16]},
    {'name': '加速度-MAX峰', 'is_v': 'V', 'address': [9, 13, 17]},
    {'name': '加速度-峭度均', 'is_v': 'V', 'address': [10, 14, 18]},
]

DATA_TYPE_IDX = {dt['name']: i for i, dt in enumerate(DATA_TYPE_DB)}


def get_data_type_from_name(name: str):
    # TODO 异常值处理
    return DATA_TYPE_DB[DATA_TYPE_IDX[name]]