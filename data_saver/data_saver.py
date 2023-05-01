# -*- coding: utf-8 -*-
# @Time    : 2023/5/1 20:58
# @Author  : XXX
# @Site    : 
# @File    : data_saver.py
# @Software: PyCharm 
# @Comment :

import csv
from datetime import datetime

from console.console_manager import ConsoleManager, ConsoleName


class DataSaver:
    instance = None

    def __init__(self, ui):
        self.ui = ui
        self.curr_file = None
        self.curr_writer = None
        self.console_manager = ConsoleManager.instance
        if not DataSaver.instance:
            DataSaver.instance = self

    @staticmethod
    def start_save():
        instance = DataSaver.instance
        name = datetime.now().strftime("%y-%m-%d-%H:%M:%S")
        instance.curr_file = open(f'data-{name}.csv', mode='w', newline='')
        instance.curr_writer = csv.writer(instance.curr_file)
        instance.console_manager.print_on(ConsoleName.DATA, f'文件{instance.curr_file.name}已创建，开始写入')

    @staticmethod
    def save_data(data):
        instance = DataSaver.instance
        for row in data:
            instance.curr_writer.writerow(row)
        instance.console_manager.print_on(ConsoleName.DATA, f'写入{len(data)}组数据')

    @staticmethod
    def finish_save():
        instance = DataSaver.instance
        if instance.curr_file:
            instance.curr_file.close()
        instance.curr_writer = None
        instance.console_manager.print_on(ConsoleName.DATA, f'写入完成，文件{instance.curr_file.name}已关闭')